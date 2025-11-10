<?php
/**
 * Court Hearing Custom Post Type
 *
 * For displaying court hearings and dates with EventON calendar plugin
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class ASEAGI_Court_Hearing_CPT {

    /**
     * Register the custom post type
     */
    public static function register() {
        $labels = array(
            'name' => __('Court Hearings', 'aseagi-wp-connector'),
            'singular_name' => __('Court Hearing', 'aseagi-wp-connector'),
            'menu_name' => __('Court Hearings', 'aseagi-wp-connector'),
            'add_new' => __('Add New Hearing', 'aseagi-wp-connector'),
            'add_new_item' => __('Add New Court Hearing', 'aseagi-wp-connector'),
            'edit_item' => __('Edit Court Hearing', 'aseagi-wp-connector'),
            'new_item' => __('New Court Hearing', 'aseagi-wp-connector'),
            'view_item' => __('View Court Hearing', 'aseagi-wp-connector'),
            'search_items' => __('Search Court Hearings', 'aseagi-wp-connector'),
            'not_found' => __('No court hearings found', 'aseagi-wp-connector'),
            'not_found_in_trash' => __('No court hearings found in trash', 'aseagi-wp-connector'),
        );

        $args = array(
            'labels' => $labels,
            'public' => true,
            'publicly_queryable' => true,
            'show_ui' => true,
            'show_in_menu' => 'aseagi-connector',
            'show_in_rest' => true,
            'query_var' => true,
            'rewrite' => array('slug' => 'court-hearing'),
            'capability_type' => 'post',
            'has_archive' => true,
            'hierarchical' => false,
            'menu_position' => null,
            'menu_icon' => 'dashicons-calendar-alt',
            'supports' => array('title', 'editor', 'excerpt', 'custom-fields'),
            'taxonomies' => array('hearing_type'),
        );

        register_post_type('court_hearing', $args);

        // Register taxonomy for hearing types
        self::register_taxonomy();

        // Register meta fields
        self::register_meta_fields();
    }

    /**
     * Register taxonomy for hearing types
     */
    private static function register_taxonomy() {
        $labels = array(
            'name' => __('Hearing Types', 'aseagi-wp-connector'),
            'singular_name' => __('Hearing Type', 'aseagi-wp-connector'),
            'search_items' => __('Search Hearing Types', 'aseagi-wp-connector'),
            'all_items' => __('All Hearing Types', 'aseagi-wp-connector'),
            'edit_item' => __('Edit Hearing Type', 'aseagi-wp-connector'),
            'update_item' => __('Update Hearing Type', 'aseagi-wp-connector'),
            'add_new_item' => __('Add New Hearing Type', 'aseagi-wp-connector'),
            'new_item_name' => __('New Hearing Type Name', 'aseagi-wp-connector'),
            'menu_name' => __('Hearing Types', 'aseagi-wp-connector'),
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

        register_taxonomy('hearing_type', array('court_hearing'), $args);

        // Create default hearing types
        self::create_default_types();
    }

    /**
     * Create default hearing types
     */
    private static function create_default_types() {
        $types = array(
            'custody-hearing' => 'Custody Hearing',
            'motion-hearing' => 'Motion Hearing',
            'status-conference' => 'Status Conference',
            'trial' => 'Trial Date',
            'mediation' => 'Mediation Session',
            'detention-hearing' => 'Detention Hearing',
            'dispositional-hearing' => 'Dispositional Hearing',
            'review-hearing' => 'Review Hearing',
            'emergency-hearing' => 'Emergency Hearing',
            'settlement-conference' => 'Settlement Conference'
        );

        foreach ($types as $slug => $name) {
            if (!term_exists($name, 'hearing_type')) {
                wp_insert_term($name, 'hearing_type', array('slug' => $slug));
            }
        }
    }

    /**
     * Register custom meta fields
     */
    private static function register_meta_fields() {
        // Hearing date
        register_post_meta('court_hearing', 'hearing_date', array(
            'type' => 'string',
            'description' => 'Hearing date in YYYY-MM-DD format',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Hearing start time
        register_post_meta('court_hearing', 'start_time', array(
            'type' => 'string',
            'description' => 'Hearing start time',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Hearing end time
        register_post_meta('court_hearing', 'end_time', array(
            'type' => 'string',
            'description' => 'Hearing end time',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Location (generalized for privacy)
        register_post_meta('court_hearing', 'location', array(
            'type' => 'string',
            'description' => 'Generalized location (e.g., "Berkeley Family Court")',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Outcome (for past hearings)
        register_post_meta('court_hearing', 'outcome', array(
            'type' => 'string',
            'description' => 'Hearing outcome (if completed)',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Outcome type
        register_post_meta('court_hearing', 'outcome_type', array(
            'type' => 'string',
            'description' => 'Outcome type: positive, negative, neutral, pending',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Significance (High/Medium/Low)
        register_post_meta('court_hearing', 'significance', array(
            'type' => 'string',
            'description' => 'Hearing significance: high, medium, low',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Status (upcoming, completed, postponed, cancelled)
        register_post_meta('court_hearing', 'status', array(
            'type' => 'string',
            'description' => 'Hearing status',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Supabase ID
        register_post_meta('court_hearing', 'supabase_id', array(
            'type' => 'integer',
            'description' => 'Supabase database ID',
            'single' => true,
            'show_in_rest' => true,
        ));

        // EventON event ID (for integration)
        register_post_meta('court_hearing', 'eventon_event_id', array(
            'type' => 'integer',
            'description' => 'EventON calendar event ID',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Public notes (filtered)
        register_post_meta('court_hearing', 'public_notes', array(
            'type' => 'string',
            'description' => 'Public-safe notes about the hearing',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Approval status
        register_post_meta('court_hearing', 'approval_status', array(
            'type' => 'string',
            'description' => 'Approval status: pending, approved, rejected',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Last synced
        register_post_meta('court_hearing', 'last_synced', array(
            'type' => 'string',
            'description' => 'Last sync timestamp',
            'single' => true,
            'show_in_rest' => true,
        ));
    }

    /**
     * Add meta boxes
     */
    public static function add_meta_boxes() {
        add_meta_box(
            'aseagi_hearing_details',
            __('Hearing Details', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_meta_box'),
            'court_hearing',
            'normal',
            'high'
        );

        add_meta_box(
            'aseagi_hearing_outcome',
            __('Hearing Outcome', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_outcome_meta_box'),
            'court_hearing',
            'normal',
            'default'
        );

        add_meta_box(
            'aseagi_hearing_sync',
            __('Sync Information', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_sync_meta_box'),
            'court_hearing',
            'side',
            'default'
        );
    }

    /**
     * Render hearing details meta box
     */
    public static function render_meta_box($post) {
        wp_nonce_field('aseagi_hearing_meta', 'aseagi_hearing_nonce');

        $hearing_date = get_post_meta($post->ID, 'hearing_date', true);
        $start_time = get_post_meta($post->ID, 'start_time', true);
        $end_time = get_post_meta($post->ID, 'end_time', true);
        $location = get_post_meta($post->ID, 'location', true);
        $significance = get_post_meta($post->ID, 'significance', true);
        $status = get_post_meta($post->ID, 'status', true);
        $public_notes = get_post_meta($post->ID, 'public_notes', true);
        $approval_status = get_post_meta($post->ID, 'approval_status', true);

        ?>
        <table class="form-table">
            <tr>
                <th><label for="hearing_date"><?php _e('Hearing Date', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="date" id="hearing_date" name="hearing_date" value="<?php echo esc_attr($hearing_date); ?>" class="regular-text" required>
                </td>
            </tr>
            <tr>
                <th><label for="start_time"><?php _e('Start Time', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="time" id="start_time" name="start_time" value="<?php echo esc_attr($start_time); ?>" class="regular-text">
                </td>
            </tr>
            <tr>
                <th><label for="end_time"><?php _e('End Time', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="time" id="end_time" name="end_time" value="<?php echo esc_attr($end_time); ?>" class="regular-text">
                </td>
            </tr>
            <tr>
                <th><label for="location"><?php _e('Location', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="text" id="location" name="location" value="<?php echo esc_attr($location); ?>" class="regular-text" placeholder="Berkeley Family Court">
                    <p class="description">Use generalized location for privacy (no specific addresses)</p>
                </td>
            </tr>
            <tr>
                <th><label for="significance"><?php _e('Significance', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <select id="significance" name="significance">
                        <option value="high" <?php selected($significance, 'high'); ?>>High</option>
                        <option value="medium" <?php selected($significance, 'medium'); ?>>Medium</option>
                        <option value="low" <?php selected($significance, 'low'); ?>>Low</option>
                    </select>
                </td>
            </tr>
            <tr>
                <th><label for="status"><?php _e('Status', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <select id="status" name="status">
                        <option value="upcoming" <?php selected($status, 'upcoming'); ?>>Upcoming</option>
                        <option value="completed" <?php selected($status, 'completed'); ?>>Completed</option>
                        <option value="postponed" <?php selected($status, 'postponed'); ?>>Postponed</option>
                        <option value="cancelled" <?php selected($status, 'cancelled'); ?>>Cancelled</option>
                    </select>
                </td>
            </tr>
            <tr>
                <th><label for="public_notes"><?php _e('Public Notes', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <textarea id="public_notes" name="public_notes" rows="4" class="large-text"><?php echo esc_textarea($public_notes); ?></textarea>
                    <p class="description">Public-safe notes (will be privacy filtered)</p>
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
     * Render outcome meta box
     */
    public static function render_outcome_meta_box($post) {
        $outcome = get_post_meta($post->ID, 'outcome', true);
        $outcome_type = get_post_meta($post->ID, 'outcome_type', true);

        ?>
        <table class="form-table">
            <tr>
                <th><label for="outcome_type"><?php _e('Outcome Type', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <select id="outcome_type" name="outcome_type">
                        <option value="pending" <?php selected($outcome_type, 'pending'); ?>>Pending</option>
                        <option value="positive" <?php selected($outcome_type, 'positive'); ?>>Positive</option>
                        <option value="negative" <?php selected($outcome_type, 'negative'); ?>>Negative</option>
                        <option value="neutral" <?php selected($outcome_type, 'neutral'); ?>>Neutral</option>
                    </select>
                </td>
            </tr>
            <tr>
                <th><label for="outcome"><?php _e('Outcome Details', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <textarea id="outcome" name="outcome" rows="6" class="large-text"><?php echo esc_textarea($outcome); ?></textarea>
                    <p class="description">Brief description of the hearing outcome (privacy filtered)</p>
                </td>
            </tr>
        </table>
        <?php
    }

    /**
     * Render sync meta box
     */
    public static function render_sync_meta_box($post) {
        $supabase_id = get_post_meta($post->ID, 'supabase_id', true);
        $eventon_event_id = get_post_meta($post->ID, 'eventon_event_id', true);
        $last_synced = get_post_meta($post->ID, 'last_synced', true);

        ?>
        <p><strong><?php _e('Supabase ID:', 'aseagi-wp-connector'); ?></strong> <?php echo $supabase_id ? esc_html($supabase_id) : 'N/A'; ?></p>
        <p><strong><?php _e('EventON Event ID:', 'aseagi-wp-connector'); ?></strong> <?php echo $eventon_event_id ? esc_html($eventon_event_id) : 'Not synced'; ?></p>
        <p><strong><?php _e('Last Synced:', 'aseagi-wp-connector'); ?></strong> <?php echo $last_synced ? esc_html($last_synced) : 'Never'; ?></p>
        <?php
    }

    /**
     * Save meta box data
     */
    public static function save_meta_box($post_id) {
        if (!isset($_POST['aseagi_hearing_nonce']) ||
            !wp_verify_nonce($_POST['aseagi_hearing_nonce'], 'aseagi_hearing_meta')) {
            return;
        }

        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }

        if (!current_user_can('edit_post', $post_id)) {
            return;
        }

        $fields = array(
            'hearing_date', 'start_time', 'end_time', 'location',
            'significance', 'status', 'public_notes', 'approval_status',
            'outcome', 'outcome_type'
        );

        foreach ($fields as $field) {
            if (isset($_POST[$field])) {
                update_post_meta($post_id, $field, sanitize_text_field($_POST[$field]));
            }
        }
    }
}

// Register hooks
add_action('add_meta_boxes', array('ASEAGI_Court_Hearing_CPT', 'add_meta_boxes'));
add_action('save_post_court_hearing', array('ASEAGI_Court_Hearing_CPT', 'save_meta_box'));
