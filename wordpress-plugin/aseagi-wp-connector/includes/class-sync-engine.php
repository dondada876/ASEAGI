<?php
/**
 * Sync Engine
 *
 * Syncs data from Supabase to WordPress custom post types
 * Applies privacy filtering and manages approval workflow
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class ASEAGI_Sync_Engine {

    /**
     * @var ASEAGI_Supabase_Client Supabase client instance
     */
    private $supabase;

    /**
     * @var ASEAGI_Privacy_Filter Privacy filter instance
     */
    private $privacy_filter;

    /**
     * @var array Sync results
     */
    private $sync_results = array();

    /**
     * Constructor
     *
     * @param ASEAGI_Supabase_Client $supabase Supabase client
     * @param ASEAGI_Privacy_Filter $privacy_filter Privacy filter
     */
    public function __construct($supabase, $privacy_filter) {
        $this->supabase = $supabase;
        $this->privacy_filter = $privacy_filter;
    }

    /**
     * Sync all data from Supabase
     *
     * @return array Sync results
     */
    public function sync_all() {
        $this->sync_results = array(
            'timeline_events' => array('synced' => 0, 'skipped' => 0, 'errors' => 0),
            'court_hearings' => array('synced' => 0, 'skipped' => 0, 'errors' => 0),
            'resources' => array('synced' => 0, 'skipped' => 0, 'errors' => 0),
            'start_time' => current_time('mysql'),
            'end_time' => null
        );

        try {
            // Sync timeline events from court_events table
            $this->sync_timeline_events();

            // Sync court hearings from court_events table
            $this->sync_court_hearings();

            // Sync resources from resources table
            $this->sync_resources();

            $this->sync_results['end_time'] = current_time('mysql');
            $this->sync_results['success'] = true;

        } catch (Exception $e) {
            $this->sync_results['success'] = false;
            $this->sync_results['error'] = $e->getMessage();
            $this->sync_results['end_time'] = current_time('mysql');
            error_log('ASEAGI Sync Error: ' . $e->getMessage());
        }

        // Save sync results for admin dashboard
        update_option('aseagi_last_sync_results', $this->sync_results);

        return $this->sync_results;
    }

    /**
     * Sync timeline events from Supabase court_events
     */
    private function sync_timeline_events() {
        $relevancy_threshold = (int) get_option('aseagi_relevancy_threshold', 700);

        // Get court events from Supabase
        $events = $this->supabase->get_timeline_events($relevancy_threshold, 100);

        if (is_wp_error($events)) {
            error_log('ASEAGI: Failed to fetch timeline events - ' . $events->get_error_message());
            $this->sync_results['timeline_events']['errors']++;
            return;
        }

        foreach ($events as $event) {
            try {
                $this->sync_single_timeline_event($event);
            } catch (Exception $e) {
                error_log('ASEAGI: Error syncing timeline event #' . $event['id'] . ' - ' . $e->getMessage());
                $this->sync_results['timeline_events']['errors']++;
            }
        }
    }

    /**
     * Sync a single timeline event
     *
     * @param array $event Event data from Supabase
     */
    private function sync_single_timeline_event($event) {
        $supabase_id = $event['id'];

        // Check if already synced
        $existing = $this->find_post_by_supabase_id('timeline_event', $supabase_id);

        // Prepare content
        $title = $event['event_title'] ?? 'Untitled Event';
        $description = $event['event_description'] ?? '';
        $event_date = $event['event_date'] ?? date('Y-m-d');
        $significance = $event['significance_score'] ?? $event['relevancy_number'] ?? 500;

        // Apply privacy filter
        $filtered_title = $this->privacy_filter->filter_content($title, 'timeline_event');
        $filtered_description = $this->privacy_filter->filter_content($description, 'timeline_event');

        // Check if content is public safe
        if (!$this->privacy_filter->is_public_safe($description, $significance)) {
            error_log('ASEAGI: Timeline event #' . $supabase_id . ' not public safe, skipping');
            $this->sync_results['timeline_events']['skipped']++;
            return;
        }

        // Prepare post data
        $post_data = array(
            'post_title' => $filtered_title,
            'post_content' => $filtered_description,
            'post_type' => 'timeline_event',
            'post_status' => get_option('aseagi_manual_approval_required', true) ? 'draft' : 'publish',
            'meta_input' => array(
                'event_date' => $event_date,
                'significance_score' => $significance,
                'supabase_id' => $supabase_id,
                'original_content' => $description,
                'approval_status' => 'pending',
                'last_synced' => current_time('mysql'),
                'timeline_icon' => $this->get_icon_for_event($event)
            )
        );

        if ($existing) {
            // Update existing post
            $post_data['ID'] = $existing->ID;
            $post_id = wp_update_post($post_data);

            if (is_wp_error($post_id)) {
                throw new Exception('Failed to update timeline event: ' . $post_id->get_error_message());
            }

            $this->sync_results['timeline_events']['synced']++;
        } else {
            // Create new post
            $post_id = wp_insert_post($post_data);

            if (is_wp_error($post_id)) {
                throw new Exception('Failed to create timeline event: ' . $post_id->get_error_message());
            }

            // Mark as synced in Supabase
            $this->supabase->mark_synced('court_events', $supabase_id, $post_id);

            $this->sync_results['timeline_events']['synced']++;
        }

        // Set category based on event type
        $this->set_timeline_category($post_id, $event);
    }

    /**
     * Sync court hearings from Supabase
     */
    private function sync_court_hearings() {
        // Get future hearings (upcoming 6 months)
        $start_date = date('Y-m-d');
        $end_date = date('Y-m-d', strtotime('+6 months'));

        $hearings = $this->supabase->get_court_hearings($start_date, $end_date);

        if (is_wp_error($hearings)) {
            error_log('ASEAGI: Failed to fetch court hearings - ' . $hearings->get_error_message());
            $this->sync_results['court_hearings']['errors']++;
            return;
        }

        foreach ($hearings as $hearing) {
            try {
                $this->sync_single_court_hearing($hearing);
            } catch (Exception $e) {
                error_log('ASEAGI: Error syncing court hearing #' . $hearing['id'] . ' - ' . $e->getMessage());
                $this->sync_results['court_hearings']['errors']++;
            }
        }
    }

    /**
     * Sync a single court hearing
     *
     * @param array $hearing Hearing data from Supabase
     */
    private function sync_single_court_hearing($hearing) {
        $supabase_id = $hearing['id'];

        // Check if already synced
        $existing = $this->find_post_by_supabase_id('court_hearing', $supabase_id);

        // Prepare content
        $title = $hearing['hearing_title'] ?? $hearing['event_title'] ?? 'Court Hearing';
        $description = $hearing['hearing_description'] ?? $hearing['event_description'] ?? '';
        $hearing_date = $hearing['hearing_date'] ?? $hearing['event_date'] ?? date('Y-m-d');
        $hearing_type = $hearing['hearing_type'] ?? 'status-conference';

        // Apply privacy filter
        $filtered_title = $this->privacy_filter->filter_content($title, 'court_hearing');
        $filtered_description = $this->privacy_filter->filter_content($description, 'court_hearing');

        // Generalize location
        $location = 'Berkeley Family Court'; // Generalized for privacy

        // Prepare post data
        $post_data = array(
            'post_title' => $filtered_title,
            'post_content' => $filtered_description,
            'post_type' => 'court_hearing',
            'post_status' => get_option('aseagi_manual_approval_required', true) ? 'draft' : 'publish',
            'meta_input' => array(
                'hearing_date' => $hearing_date,
                'start_time' => $hearing['start_time'] ?? '09:00',
                'end_time' => $hearing['end_time'] ?? '10:00',
                'location' => $location,
                'significance' => $this->get_significance_from_relevancy($hearing['relevancy_number'] ?? 500),
                'status' => 'upcoming',
                'supabase_id' => $supabase_id,
                'approval_status' => 'pending',
                'last_synced' => current_time('mysql')
            )
        );

        if ($existing) {
            // Update existing post
            $post_data['ID'] = $existing->ID;
            $post_id = wp_update_post($post_data);

            if (is_wp_error($post_id)) {
                throw new Exception('Failed to update court hearing: ' . $post_id->get_error_message());
            }

            $this->sync_results['court_hearings']['synced']++;
        } else {
            // Create new post
            $post_id = wp_insert_post($post_data);

            if (is_wp_error($post_id)) {
                throw new Exception('Failed to create court hearing: ' . $post_id->get_error_message());
            }

            // Mark as synced in Supabase
            $this->supabase->mark_synced('court_events', $supabase_id, $post_id);

            $this->sync_results['court_hearings']['synced']++;
        }

        // Set hearing type taxonomy
        wp_set_object_terms($post_id, $hearing_type, 'hearing_type');

        // If EventON is active, create calendar event
        $this->sync_to_eventon($post_id, $hearing);
    }

    /**
     * Sync resources from Supabase
     */
    private function sync_resources() {
        $resources = $this->supabase->get_resources(null, 100);

        if (is_wp_error($resources)) {
            error_log('ASEAGI: Failed to fetch resources - ' . $resources->get_error_message());
            $this->sync_results['resources']['errors']++;
            return;
        }

        foreach ($resources as $resource) {
            try {
                $this->sync_single_resource($resource);
            } catch (Exception $e) {
                error_log('ASEAGI: Error syncing resource #' . $resource['id'] . ' - ' . $e->getMessage());
                $this->sync_results['resources']['errors']++;
            }
        }
    }

    /**
     * Sync a single resource
     *
     * @param array $resource Resource data from Supabase
     */
    private function sync_single_resource($resource) {
        $supabase_id = $resource['id'];

        // Check if already synced
        $existing = $this->find_post_by_supabase_id('resource', $supabase_id);

        // Skip if not public safe
        if (!($resource['public_safe'] ?? true)) {
            $this->sync_results['resources']['skipped']++;
            return;
        }

        // Prepare content
        $title = $resource['resource_name'] ?? 'Untitled Resource';
        $description = $resource['description'] ?? '';

        // Apply privacy filter (less strict for resources)
        $filtered_description = $this->privacy_filter->filter_content($description, 'general');

        // Prepare post data
        $post_data = array(
            'post_title' => $title,
            'post_content' => $filtered_description,
            'post_type' => 'resource',
            'post_status' => 'publish', // Resources are generally pre-vetted
            'meta_input' => array(
                'contact_name' => $resource['contact_info'] ?? '',
                'contact_email' => $resource['contact_email'] ?? '',
                'contact_phone' => $resource['contact_phone'] ?? '',
                'website_url' => $resource['website_url'] ?? '',
                'address' => $resource['location'] ?? '',
                'cost' => $resource['cost'] ?? 'Unknown',
                'verified' => $resource['verified'] ?? false,
                'verified_date' => $resource['verified_date'] ?? '',
                'helpfulness_score' => $resource['relevancy_score'] ?? 500,
                'public_safe' => true,
                'supabase_id' => $supabase_id,
                'last_synced' => current_time('mysql')
            )
        );

        if ($existing) {
            // Update existing post
            $post_data['ID'] = $existing->ID;
            $post_id = wp_update_post($post_data);

            if (is_wp_error($post_id)) {
                throw new Exception('Failed to update resource: ' . $post_id->get_error_message());
            }

            $this->sync_results['resources']['synced']++;
        } else {
            // Create new post
            $post_id = wp_insert_post($post_data);

            if (is_wp_error($post_id)) {
                throw new Exception('Failed to create resource: ' . $post_id->get_error_message());
            }

            // Mark as synced in Supabase
            $this->supabase->mark_synced('resources', $supabase_id, $post_id);

            $this->sync_results['resources']['synced']++;
        }

        // Set resource type taxonomy
        $resource_type = $resource['resource_type'] ?? 'other';
        wp_set_object_terms($post_id, $resource_type, 'resource_type');

        // If ListingPro is active, sync to directory
        $this->sync_to_listingpro($post_id, $resource);
    }

    /**
     * Find WordPress post by Supabase ID
     *
     * @param string $post_type Post type
     * @param int $supabase_id Supabase ID
     * @return WP_Post|null Post object or null
     */
    private function find_post_by_supabase_id($post_type, $supabase_id) {
        $posts = get_posts(array(
            'post_type' => $post_type,
            'meta_key' => 'supabase_id',
            'meta_value' => $supabase_id,
            'posts_per_page' => 1,
            'post_status' => 'any'
        ));

        return !empty($posts) ? $posts[0] : null;
    }

    /**
     * Set timeline event category based on event data
     *
     * @param int $post_id Post ID
     * @param array $event Event data
     */
    private function set_timeline_category($post_id, $event) {
        $relevancy = $event['relevancy_number'] ?? $event['significance_score'] ?? 500;
        $event_type = $event['event_type'] ?? '';

        // Determine category based on relevancy and type
        if ($relevancy >= 900) {
            $category = 'evidence-discoveries'; // Smoking gun
        } elseif ($relevancy >= 800) {
            $category = 'legal-victories'; // Strong evidence
        } elseif (stripos($event_type, 'hearing') !== false) {
            $category = 'court-hearings';
        } elseif (stripos($event_type, 'cps') !== false) {
            $category = 'cps-actions';
        } elseif (stripos($event_type, 'filing') !== false) {
            $category = 'document-filings';
        } else {
            $category = 'milestones';
        }

        wp_set_object_terms($post_id, $category, 'timeline_event_category');
    }

    /**
     * Get Font Awesome icon for event
     *
     * @param array $event Event data
     * @return string Icon class
     */
    private function get_icon_for_event($event) {
        $relevancy = $event['relevancy_number'] ?? 500;
        $event_type = $event['event_type'] ?? '';

        if ($relevancy >= 900) {
            return 'fa-star'; // Smoking gun
        } elseif (stripos($event_type, 'hearing') !== false) {
            return 'fa-gavel';
        } elseif (stripos($event_type, 'filing') !== false) {
            return 'fa-file-text';
        } elseif (stripos($event_type, 'evidence') !== false) {
            return 'fa-folder-open';
        } else {
            return 'fa-flag';
        }
    }

    /**
     * Convert relevancy score to significance level
     *
     * @param int $relevancy Relevancy score (0-1000)
     * @return string Significance level (high/medium/low)
     */
    private function get_significance_from_relevancy($relevancy) {
        if ($relevancy >= 800) {
            return 'high';
        } elseif ($relevancy >= 600) {
            return 'medium';
        } else {
            return 'low';
        }
    }

    /**
     * Sync court hearing to EventON calendar
     *
     * @param int $post_id WordPress post ID
     * @param array $hearing Hearing data
     */
    private function sync_to_eventon($post_id, $hearing) {
        // Check if EventON is active
        if (!class_exists('EventON')) {
            return;
        }

        // EventON integration logic would go here
        // This would create/update an EventON event linked to this court hearing
        // For now, we just log that it's ready for EventON sync

        update_post_meta($post_id, 'eventon_sync_pending', true);
    }

    /**
     * Sync resource to ListingPro directory
     *
     * @param int $post_id WordPress post ID
     * @param array $resource Resource data
     */
    private function sync_to_listingpro($post_id, $resource) {
        // Check if ListingPro is active
        if (!function_exists('listingpro_init')) {
            return;
        }

        // ListingPro integration logic would go here
        // This would create/update a ListingPro listing linked to this resource
        // For now, we just log that it's ready for ListingPro sync

        update_post_meta($post_id, 'listingpro_sync_pending', true);
    }

    /**
     * Get sync statistics
     *
     * @return array Statistics
     */
    public function get_sync_stats() {
        $last_results = get_option('aseagi_last_sync_results', array());

        return array(
            'last_sync' => get_option('aseagi_last_sync', 0),
            'last_results' => $last_results,
            'pending_approval_count' => $this->get_pending_approval_count(),
            'total_synced' => $this->get_total_synced_count()
        );
    }

    /**
     * Get count of posts pending approval
     *
     * @return int Count
     */
    private function get_pending_approval_count() {
        $count = 0;

        $post_types = array('timeline_event', 'court_hearing', 'resource');

        foreach ($post_types as $post_type) {
            $posts = get_posts(array(
                'post_type' => $post_type,
                'post_status' => 'draft',
                'meta_query' => array(
                    array(
                        'key' => 'approval_status',
                        'value' => 'pending'
                    )
                ),
                'posts_per_page' => -1
            ));

            $count += count($posts);
        }

        return $count;
    }

    /**
     * Get total count of synced posts
     *
     * @return int Count
     */
    private function get_total_synced_count() {
        $count = 0;

        $post_types = array('timeline_event', 'court_hearing', 'resource');

        foreach ($post_types as $post_type) {
            $posts = get_posts(array(
                'post_type' => $post_type,
                'post_status' => 'any',
                'meta_key' => 'supabase_id',
                'posts_per_page' => -1
            ));

            $count += count($posts);
        }

        return $count;
    }

    /**
     * Manual sync trigger for admin
     *
     * @return array Sync results
     */
    public function manual_sync() {
        // Log manual sync
        error_log('ASEAGI: Manual sync triggered by user ' . get_current_user_id());

        return $this->sync_all();
    }
}
