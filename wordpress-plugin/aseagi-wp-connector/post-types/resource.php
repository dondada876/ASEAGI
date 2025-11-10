<?php
/**
 * Resource Custom Post Type
 *
 * For displaying legal resources and support services with ListingPro directory
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class ASEAGI_Resource_CPT {

    /**
     * Register the custom post type
     */
    public static function register() {
        $labels = array(
            'name' => __('Resources', 'aseagi-wp-connector'),
            'singular_name' => __('Resource', 'aseagi-wp-connector'),
            'menu_name' => __('Resources', 'aseagi-wp-connector'),
            'add_new' => __('Add New Resource', 'aseagi-wp-connector'),
            'add_new_item' => __('Add New Resource', 'aseagi-wp-connector'),
            'edit_item' => __('Edit Resource', 'aseagi-wp-connector'),
            'new_item' => __('New Resource', 'aseagi-wp-connector'),
            'view_item' => __('View Resource', 'aseagi-wp-connector'),
            'search_items' => __('Search Resources', 'aseagi-wp-connector'),
            'not_found' => __('No resources found', 'aseagi-wp-connector'),
            'not_found_in_trash' => __('No resources found in trash', 'aseagi-wp-connector'),
        );

        $args = array(
            'labels' => $labels,
            'public' => true,
            'publicly_queryable' => true,
            'show_ui' => true,
            'show_in_menu' => 'aseagi-connector',
            'show_in_rest' => true,
            'query_var' => true,
            'rewrite' => array('slug' => 'resource'),
            'capability_type' => 'post',
            'has_archive' => true,
            'hierarchical' => false,
            'menu_position' => null,
            'menu_icon' => 'dashicons-book',
            'supports' => array('title', 'editor', 'thumbnail', 'excerpt', 'custom-fields'),
            'taxonomies' => array('resource_type', 'resource_location'),
        );

        register_post_type('resource', $args);

        // Register taxonomies
        self::register_taxonomies();

        // Register meta fields
        self::register_meta_fields();
    }

    /**
     * Register taxonomies
     */
    private static function register_taxonomies() {
        // Resource Type taxonomy
        $type_labels = array(
            'name' => __('Resource Types', 'aseagi-wp-connector'),
            'singular_name' => __('Resource Type', 'aseagi-wp-connector'),
            'search_items' => __('Search Resource Types', 'aseagi-wp-connector'),
            'all_items' => __('All Resource Types', 'aseagi-wp-connector'),
            'edit_item' => __('Edit Resource Type', 'aseagi-wp-connector'),
            'update_item' => __('Update Resource Type', 'aseagi-wp-connector'),
            'add_new_item' => __('Add New Resource Type', 'aseagi-wp-connector'),
            'new_item_name' => __('New Resource Type Name', 'aseagi-wp-connector'),
            'menu_name' => __('Resource Types', 'aseagi-wp-connector'),
        );

        register_taxonomy('resource_type', array('resource'), array(
            'labels' => $type_labels,
            'hierarchical' => true,
            'public' => true,
            'show_ui' => true,
            'show_admin_column' => true,
            'show_in_nav_menus' => true,
            'show_in_rest' => true,
        ));

        // Resource Location taxonomy
        $location_labels = array(
            'name' => __('Locations', 'aseagi-wp-connector'),
            'singular_name' => __('Location', 'aseagi-wp-connector'),
            'search_items' => __('Search Locations', 'aseagi-wp-connector'),
            'all_items' => __('All Locations', 'aseagi-wp-connector'),
            'edit_item' => __('Edit Location', 'aseagi-wp-connector'),
            'update_item' => __('Update Location', 'aseagi-wp-connector'),
            'add_new_item' => __('Add New Location', 'aseagi-wp-connector'),
            'new_item_name' => __('New Location Name', 'aseagi-wp-connector'),
            'menu_name' => __('Locations', 'aseagi-wp-connector'),
        );

        register_taxonomy('resource_location', array('resource'), array(
            'labels' => $location_labels,
            'hierarchical' => true,
            'public' => true,
            'show_ui' => true,
            'show_admin_column' => true,
            'show_in_nav_menus' => true,
            'show_in_rest' => true,
        ));

        // Create default types and locations
        self::create_defaults();
    }

    /**
     * Create default resource types and locations
     */
    private static function create_defaults() {
        // Resource types
        $types = array(
            'legal-services' => array(
                'name' => 'Legal Services',
                'description' => 'Attorneys, legal aid, and legal assistance'
            ),
            'support-services' => array(
                'name' => 'Support Services',
                'description' => 'Counseling, therapy, and support groups'
            ),
            'government-agencies' => array(
                'name' => 'Government Agencies',
                'description' => 'CPS, courts, and government offices'
            ),
            'advocacy-organizations' => array(
                'name' => 'Advocacy Organizations',
                'description' => 'Family rights and advocacy groups'
            ),
            'educational-resources' => array(
                'name' => 'Educational Resources',
                'description' => 'Information and educational materials'
            ),
            'financial-assistance' => array(
                'name' => 'Financial Assistance',
                'description' => 'Legal funds and financial support'
            ),
            'housing-assistance' => array(
                'name' => 'Housing Assistance',
                'description' => 'Shelter and housing support'
            ),
            'mental-health' => array(
                'name' => 'Mental Health Services',
                'description' => 'Mental health and wellness support'
            )
        );

        foreach ($types as $slug => $type) {
            if (!term_exists($type['name'], 'resource_type')) {
                wp_insert_term($type['name'], 'resource_type', array(
                    'slug' => $slug,
                    'description' => $type['description']
                ));
            }
        }

        // Locations (Bay Area focused but expandable)
        $locations = array(
            'berkeley' => 'Berkeley',
            'oakland' => 'Oakland',
            'san-francisco' => 'San Francisco',
            'alameda-county' => 'Alameda County',
            'bay-area' => 'Bay Area',
            'california' => 'California',
            'online' => 'Online/Virtual',
            'nationwide' => 'Nationwide'
        );

        foreach ($locations as $slug => $name) {
            if (!term_exists($name, 'resource_location')) {
                wp_insert_term($name, 'resource_location', array('slug' => $slug));
            }
        }
    }

    /**
     * Register custom meta fields
     */
    private static function register_meta_fields() {
        // Contact information
        register_post_meta('resource', 'contact_name', array(
            'type' => 'string',
            'description' => 'Contact person or organization name',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'contact_phone', array(
            'type' => 'string',
            'description' => 'Contact phone number',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'contact_email', array(
            'type' => 'string',
            'description' => 'Contact email address',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'website_url', array(
            'type' => 'string',
            'description' => 'Website URL',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'address', array(
            'type' => 'string',
            'description' => 'Physical address (generalized)',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Resource details
        register_post_meta('resource', 'cost', array(
            'type' => 'string',
            'description' => 'Cost information (e.g., "Free", "$50/hour", "Sliding scale")',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'eligibility', array(
            'type' => 'string',
            'description' => 'Eligibility requirements',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'hours', array(
            'type' => 'string',
            'description' => 'Hours of operation',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'languages', array(
            'type' => 'string',
            'description' => 'Languages spoken',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Verification and rating
        register_post_meta('resource', 'verified', array(
            'type' => 'boolean',
            'description' => 'Whether resource has been verified',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'verified_date', array(
            'type' => 'string',
            'description' => 'Date resource was verified',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'verified_by', array(
            'type' => 'string',
            'description' => 'Who verified the resource',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'rating', array(
            'type' => 'number',
            'description' => 'User rating (1-5 stars)',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'review_count', array(
            'type' => 'integer',
            'description' => 'Number of reviews',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Helpfulness score
        register_post_meta('resource', 'helpfulness_score', array(
            'type' => 'integer',
            'description' => 'Helpfulness score (0-1000)',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Supabase sync
        register_post_meta('resource', 'supabase_id', array(
            'type' => 'integer',
            'description' => 'Supabase database ID',
            'single' => true,
            'show_in_rest' => true,
        ));

        register_post_meta('resource', 'last_synced', array(
            'type' => 'string',
            'description' => 'Last sync timestamp',
            'single' => true,
            'show_in_rest' => true,
        ));

        // Public safety
        register_post_meta('resource', 'public_safe', array(
            'type' => 'boolean',
            'description' => 'Whether resource is safe for public display',
            'single' => true,
            'show_in_rest' => true,
        ));

        // ListingPro compatibility
        register_post_meta('resource', 'listing_pro_id', array(
            'type' => 'integer',
            'description' => 'ListingPro listing ID',
            'single' => true,
            'show_in_rest' => true,
        ));
    }

    /**
     * Add meta boxes
     */
    public static function add_meta_boxes() {
        add_meta_box(
            'aseagi_resource_contact',
            __('Contact Information', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_contact_meta_box'),
            'resource',
            'normal',
            'high'
        );

        add_meta_box(
            'aseagi_resource_details',
            __('Resource Details', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_details_meta_box'),
            'resource',
            'normal',
            'default'
        );

        add_meta_box(
            'aseagi_resource_verification',
            __('Verification & Rating', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_verification_meta_box'),
            'resource',
            'side',
            'default'
        );

        add_meta_box(
            'aseagi_resource_sync',
            __('Sync Information', 'aseagi-wp-connector'),
            array(__CLASS__, 'render_sync_meta_box'),
            'resource',
            'side',
            'low'
        );
    }

    /**
     * Render contact info meta box
     */
    public static function render_contact_meta_box($post) {
        wp_nonce_field('aseagi_resource_meta', 'aseagi_resource_nonce');

        $contact_name = get_post_meta($post->ID, 'contact_name', true);
        $contact_phone = get_post_meta($post->ID, 'contact_phone', true);
        $contact_email = get_post_meta($post->ID, 'contact_email', true);
        $website_url = get_post_meta($post->ID, 'website_url', true);
        $address = get_post_meta($post->ID, 'address', true);

        ?>
        <table class="form-table">
            <tr>
                <th><label for="contact_name"><?php _e('Contact Name', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="text" id="contact_name" name="contact_name" value="<?php echo esc_attr($contact_name); ?>" class="regular-text">
                </td>
            </tr>
            <tr>
                <th><label for="contact_phone"><?php _e('Phone', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="tel" id="contact_phone" name="contact_phone" value="<?php echo esc_attr($contact_phone); ?>" class="regular-text">
                </td>
            </tr>
            <tr>
                <th><label for="contact_email"><?php _e('Email', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="email" id="contact_email" name="contact_email" value="<?php echo esc_attr($contact_email); ?>" class="regular-text">
                </td>
            </tr>
            <tr>
                <th><label for="website_url"><?php _e('Website', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="url" id="website_url" name="website_url" value="<?php echo esc_attr($website_url); ?>" class="regular-text">
                </td>
            </tr>
            <tr>
                <th><label for="address"><?php _e('Address', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="text" id="address" name="address" value="<?php echo esc_attr($address); ?>" class="large-text" placeholder="Berkeley, CA (generalized)">
                    <p class="description">Use generalized address for privacy</p>
                </td>
            </tr>
        </table>
        <?php
    }

    /**
     * Render details meta box
     */
    public static function render_details_meta_box($post) {
        $cost = get_post_meta($post->ID, 'cost', true);
        $eligibility = get_post_meta($post->ID, 'eligibility', true);
        $hours = get_post_meta($post->ID, 'hours', true);
        $languages = get_post_meta($post->ID, 'languages', true);
        $helpfulness_score = get_post_meta($post->ID, 'helpfulness_score', true);

        ?>
        <table class="form-table">
            <tr>
                <th><label for="cost"><?php _e('Cost', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="text" id="cost" name="cost" value="<?php echo esc_attr($cost); ?>" class="regular-text" placeholder="Free, Sliding scale, $50/hour">
                </td>
            </tr>
            <tr>
                <th><label for="eligibility"><?php _e('Eligibility', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <textarea id="eligibility" name="eligibility" rows="3" class="large-text"><?php echo esc_textarea($eligibility); ?></textarea>
                    <p class="description">Who qualifies for this resource</p>
                </td>
            </tr>
            <tr>
                <th><label for="hours"><?php _e('Hours', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="text" id="hours" name="hours" value="<?php echo esc_attr($hours); ?>" class="regular-text" placeholder="Mon-Fri 9am-5pm">
                </td>
            </tr>
            <tr>
                <th><label for="languages"><?php _e('Languages', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="text" id="languages" name="languages" value="<?php echo esc_attr($languages); ?>" class="regular-text" placeholder="English, Spanish">
                </td>
            </tr>
            <tr>
                <th><label for="helpfulness_score"><?php _e('Helpfulness Score', 'aseagi-wp-connector'); ?></label></th>
                <td>
                    <input type="number" id="helpfulness_score" name="helpfulness_score" value="<?php echo esc_attr($helpfulness_score); ?>" min="0" max="1000" class="small-text">
                    <p class="description">0-1000 (higher = more helpful)</p>
                </td>
            </tr>
        </table>
        <?php
    }

    /**
     * Render verification meta box
     */
    public static function render_verification_meta_box($post) {
        $verified = get_post_meta($post->ID, 'verified', true);
        $verified_date = get_post_meta($post->ID, 'verified_date', true);
        $verified_by = get_post_meta($post->ID, 'verified_by', true);
        $rating = get_post_meta($post->ID, 'rating', true);
        $review_count = get_post_meta($post->ID, 'review_count', true);
        $public_safe = get_post_meta($post->ID, 'public_safe', true);

        ?>
        <p>
            <label>
                <input type="checkbox" name="verified" value="1" <?php checked($verified, true); ?>>
                <?php _e('Verified Resource', 'aseagi-wp-connector'); ?>
            </label>
        </p>
        <?php if ($verified): ?>
        <p><strong><?php _e('Verified Date:', 'aseagi-wp-connector'); ?></strong> <?php echo esc_html($verified_date); ?></p>
        <p><strong><?php _e('Verified By:', 'aseagi-wp-connector'); ?></strong> <?php echo esc_html($verified_by); ?></p>
        <?php endif; ?>
        <hr>
        <p>
            <label for="rating"><?php _e('Rating:', 'aseagi-wp-connector'); ?></label><br>
            <input type="number" id="rating" name="rating" value="<?php echo esc_attr($rating); ?>" min="0" max="5" step="0.1" class="small-text"> / 5
        </p>
        <p>
            <label for="review_count"><?php _e('Reviews:', 'aseagi-wp-connector'); ?></label><br>
            <input type="number" id="review_count" name="review_count" value="<?php echo esc_attr($review_count); ?>" min="0" class="small-text">
        </p>
        <hr>
        <p>
            <label>
                <input type="checkbox" name="public_safe" value="1" <?php checked($public_safe, true); ?>>
                <?php _e('Public Safe', 'aseagi-wp-connector'); ?>
            </label>
        </p>
        <?php
    }

    /**
     * Render sync meta box
     */
    public static function render_sync_meta_box($post) {
        $supabase_id = get_post_meta($post->ID, 'supabase_id', true);
        $listing_pro_id = get_post_meta($post->ID, 'listing_pro_id', true);
        $last_synced = get_post_meta($post->ID, 'last_synced', true);

        ?>
        <p><strong><?php _e('Supabase ID:', 'aseagi-wp-connector'); ?></strong> <?php echo $supabase_id ? esc_html($supabase_id) : 'N/A'; ?></p>
        <p><strong><?php _e('ListingPro ID:', 'aseagi-wp-connector'); ?></strong> <?php echo $listing_pro_id ? esc_html($listing_pro_id) : 'Not synced'; ?></p>
        <p><strong><?php _e('Last Synced:', 'aseagi-wp-connector'); ?></strong> <?php echo $last_synced ? esc_html($last_synced) : 'Never'; ?></p>
        <?php
    }

    /**
     * Save meta box data
     */
    public static function save_meta_box($post_id) {
        if (!isset($_POST['aseagi_resource_nonce']) ||
            !wp_verify_nonce($_POST['aseagi_resource_nonce'], 'aseagi_resource_meta')) {
            return;
        }

        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }

        if (!current_user_can('edit_post', $post_id)) {
            return;
        }

        // Save text fields
        $text_fields = array(
            'contact_name', 'contact_phone', 'contact_email', 'website_url', 'address',
            'cost', 'eligibility', 'hours', 'languages', 'helpfulness_score',
            'verified_date', 'verified_by', 'rating', 'review_count'
        );

        foreach ($text_fields as $field) {
            if (isset($_POST[$field])) {
                update_post_meta($post_id, $field, sanitize_text_field($_POST[$field]));
            }
        }

        // Save boolean fields
        update_post_meta($post_id, 'verified', isset($_POST['verified']) ? true : false);
        update_post_meta($post_id, 'public_safe', isset($_POST['public_safe']) ? true : false);

        // If just verified, set verification date and user
        if (isset($_POST['verified']) && $_POST['verified']) {
            $current_user = wp_get_current_user();
            update_post_meta($post_id, 'verified_date', current_time('Y-m-d'));
            update_post_meta($post_id, 'verified_by', $current_user->display_name);
        }
    }
}

// Register hooks
add_action('add_meta_boxes', array('ASEAGI_Resource_CPT', 'add_meta_boxes'));
add_action('save_post_resource', array('ASEAGI_Resource_CPT', 'save_meta_box'));
