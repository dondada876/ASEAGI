<?php
/**
 * Timeline Event Custom Post Type
 *
 * For displaying court events chronologically with Cool Timeline Pro
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class ASEAGI_Timeline_Event_CPT {

    /**
     * Register the custom post type
     */
    public static function register() {
        $labels = array(
            'name' => __('Timeline Events', 'aseagi-wp-connector'),
            'singular_name' => __('Timeline Event', 'aseagi-wp-connector'),
            'menu_name' => __('Timeline Events', 'aseagi-wp-connector'),
            'add_new' => __('Add New Event', 'aseagi-wp-connector'),
            'add_new_item' => __('Add New Timeline Event', 'aseagi-wp-connector'),
            'edit_item' => __('Edit Timeline Event', 'aseagi-wp-connector'),
            'new_item' => __('New Timeline Event', 'aseagi-wp-connector'),
            'view_item' => __('View Timeline Event', 'aseagi-wp-connector'),
            'search_items' => __('Search Timeline Events', 'aseagi-wp-connector'),
            'not_found' => __('No timeline events found', 'aseagi-wp-connector'),
            'not_found_in_trash' => __('No timeline events found in trash', 'aseagi-wp-connector'),
        );

        $args = array(
            'labels' => $labels,
            'public' => true,
            'publicly_queryable' => true,
            'show_ui' => true,
            'show_in_menu' => 'aseagi-connector',
            'show_in_rest' => true,
            'query_var' => true,
            'rewrite' => array('slug' => 'timeline-event'),
            'capability_type' => 'post',
            'has_archive' => true,
            'hierarchical' => false,
            'menu_position' => null,
            'menu_icon' => 'dashicons-timeline',
            'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
            'taxonomies' => array('timeline_event_category'),
        );

        register_post_type('timeline_event', $args);

        // Register taxonomy for event categories
        self::register_taxonomy();

        // Register meta fields
        self::register_meta_fields();
    }

    /**
     * Register taxonomy for timeline event categories
     */
    private static function register_taxonomy() {
        $labels = array(
            'name' => __('Event Categories', 'aseagi-wp-connector'),
            'singular_name' => __('Event Category', 'aseagi-wp-connector'),
            'search_items' => __('Search Event Categories', 'aseagi-wp-connector'),
            'all_items' => __('All Event Categories', 'aseagi-wp-connector'),
            'edit_item' => __('Edit Event Category', 'aseagi-wp-connector'),
            'update_item' => __('Update Event Category', 'aseagi-wp-connector'),
            'add_new_item' => __('Add New Event Category', 'aseagi-wp-connector'),
            'new_item_name' => __('New Event Category Name', 'aseagi-wp-connector'),
            'menu_name' => __('Event Categories', 'aseagi-wp-connector'),
        );

        $args = array(
            'labels' => $labels,
            'hierarchical' => true,
            'public' => true,
            'show_ui' => true,
            'show_admin_column' => true,
            'show_in_nav_menus' => true,
            'show_tagcloud' => false,
            'show_in_rest' => true,
        );

        register_taxonomy('timeline_event_category', array('timeline_event'), $args);

        // Create default categories for Cool Timeline Pro
        self::create_default_categories();
    }

    /**
     * Create default event categories
     */
    private static function create_default_categories() {
        $categories = array(
            'court-hearings' => array(
                'name' => 'Court Hearings',
                'description' => 'Court hearings and legal proceedings',
                'color' => '#e74c3c' // Red
            ),
            'legal-victories' => array(
                'name' => 'Legal Victories',
                'description' => 'Positive outcomes and victories in the case',
                'color' => '#27ae60' // Green
            ),
            'cps-actions' => array(
                'name' => 'CPS Actions',
                'description' => 'Child Protective Services actions and decisions',
                'color' => '#f39c12' // Orange
            ),
            'document-filings' => array(
                'name' => 'Document Filings',
                'description' => 'Important document submissions and filings',
                'color' => '#3498db' // Blue
            ),
            'milestones' => array(
                'name' => 'Milestones',
                'description' => 'Case milestones and significant events',
                'color' => '#9b59b6' // Purple
            ),
            'evidence-discoveries' => array(
                'name' => 'Evidence Discoveries',
                'description' => 'Smoking gun evidence and critical discoveries',
                'color' => '#1abc9c' // Teal
            )
        );

        foreach ($categories as $slug => $category) {
            if (!term_exists($category['name'], 'timeline_event_category')) {
                $term = wp_insert_term($category['name'], 'timeline_event_category', array(
                    'slug' => $slug,
                    'description' => $category['description']
                ));

                // Store color as term meta
                if (!is_wp_error($term)) {
                    add_term_meta($term['term_id'], 'event_color', $category['color'], true);
                }
            }
        }
    }

    /**
     * Register custom meta fields
     */
    private static function register_meta_fields() {
        // Event date
        register_post_meta('timeline_event', 'event_date', array(
            'type' => 'string',
            'description' => 'Event date in YYYY-MM-DD format',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Event time
        register_post_meta('timeline_event', 'event_time', array(
            'type' => 'string',
            'description' => 'Event time',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Significance score (0-1000, PROJ344 compatible)
        register_post_meta('timeline_event', 'significance_score', array(
            'type' => 'integer',
            'description' => 'Event significance score (0-1000)',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Supabase ID (for tracking sync)
        register_post_meta('timeline_event', 'supabase_id', array(
            'type' => 'integer',
            'description' => 'Supabase database ID',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Original content (before privacy filtering)
        register_post_meta('timeline_event', 'original_content', array(
            'type' => 'string',
            'description' => 'Original content before privacy filtering',
            'single' => true,
            'show_in_rest' => false, // Don't expose via REST API
        ));

        // Redaction log
        register_post_meta('timeline_event', 'redaction_log', array(
            'type' => 'string',
            'description' => 'JSON log of redactions made',
            'single' => true,
            'show_in_rest' => false,
        ));

        // Manual approval status
        register_post_meta('timeline_event', 'approval_status', array(
            'type' => 'string',
            'description' => 'Approval status: pending, approved, rejected',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Last synced timestamp
        register_post_meta('timeline_event', 'last_synced', array(
            'type' => 'string',
            'description' => 'Last sync timestamp',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Icon for Cool Timeline Pro
        register_post_meta('timeline_event', 'timeline_icon', array(
            'type' => 'string',
            'description' => 'Font Awesome icon class',
            'single' => true,
            'show_in_rest' => true,
        ));
    }

    /**
     * Add meta boxes for timeline events
     */
    public static function add_meta_boxes() {
        add_meta_box(
            'aseagi_timeline_event_details',
            __('Event Details', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_meta_box'),
            'timeline_event',
            'normal',
            'high'
        );

        add_meta_box(
            'aseagi_timeline_sync_info',
            __('Sync Information', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_sync_meta_box'),
            'timeline_event',
            'side',
            'default'
        );
    }

    /**
     * Render event details meta box
     */
    public static function render_meta_box($post) {
        wp_nonce_field('aseagi_timeline_event_meta', 'aseagi_timeline_event_nonce');

        $event_date = get_post_meta($post->ID, 'event_date', true);
        $event_time = get_post_meta($post->ID, 'event_time', true);
        $significance_score = get_post_meta($post->ID, 'significance_score', true);
        $timeline_icon = get_post_meta($post->ID, 'timeline_icon', true);
        $approval_status = get_post_meta($post->ID, 'approval_status', true);

        ?>
        <table class="form-table">
            <tr>
                <th><label for="event_date"><?php _e('Event Date', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="date" id="event_date" name="event_date" value="<?php echo esc_attr($event_date); ?>" class="regular-text" required>
                </td>
            </tr>
            <tr>
                <th><label for="event_time"><?php _e('Event Time', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="time" id="event_time" name="event_time" value="<?php echo esc_attr($event_time); ?>" class="regular-text">
                </td>
            </tr>
            <tr>
                <th><label for="significance_score"><?php _e('Significance Score', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="number" id="significance_score" name="significance_score" value="<?php echo esc_attr($significance_score); ?>" min="0" max="1000" class="small-text">
                    <p class="description">0-1000 (900+ = smoking gun, 800-899 = high, 700-799 = important)</p>
                </td>
            </tr>
            <tr>
                <th><label for="timeline_icon"><?php _e('Timeline Icon', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="text" id="timeline_icon" name="timeline_icon" value="<?php echo esc_attr($timeline_icon); ?>" class="regular-text" placeholder="fa-gavel">
                    <p class="description">Font Awesome icon class (e.g., fa-gavel, fa-file-text, fa-flag)</p>
                </td>
            </tr>
            <tr>
                <th><label for="approval_status"><?php _e('Approval Status', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <select id="approval_status" name="approval_status">
                        <option value="pending" <?php selected($approval_status, 'pending'); ?>>Pending Review</option>
                        <option value="approved" <?php selected($approval_status, 'approved'); ?>>Approved</option>
                        <option value="rejected" <?php selected($approval_status, 'rejected'); ?>>Rejected</option>
                    </select>
                </td>
            </tr>
        </table>
        <?php
    }

    /**
     * Render sync information meta box
     */
    public static function render_sync_meta_box($post) {
        $supabase_id = get_post_meta($post->ID, 'supabase_id', true);
        $last_synced = get_post_meta($post->ID, 'last_synced', true);

        ?>
        <p><strong><?php _e('Supabase ID:', 'aseagi-wp-connector'); ?></strong> <?php echo $supabase_id ? esc_html($supabase_id) : 'N/A'; ?></p>
        <p><strong><?php _e('Last Synced:', 'aseagi-wp-connector'); ?></strong> <?php echo $last_synced ? esc_html($last_synced) : 'Never'; ?></p>
        <?php
    }

    /**
     * Save meta box data
     */
    public static function save_meta_box($post_id) {
        // Check nonce
        if (!isset($_POST['aseagi_timeline_event_nonce']) ||
            !wp_verify_nonce($_POST['aseagi_timeline_event_nonce'], 'aseagi_timeline_event_meta')) {
            return;
        }

        // Check autosave
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }

        // Check permissions
        if (!current_user_can('edit_post', $post_id)) {
            return;
        }

        // Save fields
        $fields = array('event_date', 'event_time', 'significance_score', 'timeline_icon', 'approval_status');

        foreach ($fields as $field) {
            if (isset($_POST[$field])) {
                update_post_meta($post_id, $field, sanitize_text_field($_POST[$field]));
            }
        }
    }
}

// Register hooks
add_action('add_meta_boxes', array('ASEAGI_Timeline_Event_CPT', 'add_meta_boxes'));
add_action('save_post_timeline_event', array('ASEAGI_Timeline_Event_CPT', 'save_meta_box'));
