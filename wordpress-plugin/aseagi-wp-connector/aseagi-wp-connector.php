<?php
/**
 * Plugin Name: ASEAGI WordPress Connector
 * Plugin URI: https://github.com/dondada876/ASEAGI
 * Description: Connects WordPress to ASEAGI Supabase database for public legal case storytelling. Integrates with Cool Timeline Pro, EventON, and ListingPro.
 * Version: 1.0.0
 * Author: ASEAGI Project
 * Author URI: https://github.com/dondada876/ASEAGI
 * License: MIT
 * Text Domain: aseagi-wp-connector
 *
 * For Ashe. For Justice. For All Children. 🛡️
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('ASEAGI_WP_VERSION', '1.0.0');
define('ASEAGI_WP_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('ASEAGI_WP_PLUGIN_URL', plugin_dir_url(__FILE__));
define('ASEAGI_WP_PLUGIN_FILE', __FILE__);

/**
 * Main ASEAGI WP Connector Class
 */
class ASEAGI_WP_Connector {

    /**
     * @var ASEAGI_WP_Connector Singleton instance
     */
    private static $instance = null;

    /**
     * @var object Supabase client instance
     */
    public $supabase;

    /**
     * @var object Privacy filter instance
     */
    public $privacy_filter;

    /**
     * @var object Sync engine instance
     */
    public $sync_engine;

    /**
     * Get singleton instance
     */
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * Constructor
     */
    private function __construct() {
        // Load dependencies
        $this->load_dependencies();

        // Initialize components
        $this->init_components();

        // Register hooks
        $this->register_hooks();
    }

    /**
     * Load plugin dependencies
     */
    private function load_dependencies() {
        // Core classes
        require_once ASEAGI_WP_PLUGIN_DIR . 'includes/class-supabase-client.php';
        require_once ASEAGI_WP_PLUGIN_DIR . 'includes/class-privacy-filter.php';
        require_once ASEAGI_WP_PLUGIN_DIR . 'includes/class-sync-engine.php';
        require_once ASEAGI_WP_PLUGIN_DIR . 'includes/class-admin-dashboard.php';

        // Custom post types
        require_once ASEAGI_WP_PLUGIN_DIR . 'post-types/timeline-event.php';
        require_once ASEAGI_WP_PLUGIN_DIR . 'post-types/court-hearing.php';
        require_once ASEAGI_WP_PLUGIN_DIR . 'post-types/resource.php';
    }

    /**
     * Initialize plugin components
     */
    private function init_components() {
        // Initialize Supabase client
        $supabase_url = get_option('aseagi_supabase_url', '');
        $supabase_key = get_option('aseagi_supabase_service_key', '');

        if (!empty($supabase_url) && !empty($supabase_key)) {
            $this->supabase = new ASEAGI_Supabase_Client($supabase_url, $supabase_key);
        }

        // Initialize privacy filter
        $this->privacy_filter = new ASEAGI_Privacy_Filter();

        // Initialize sync engine
        if ($this->supabase) {
            $this->sync_engine = new ASEAGI_Sync_Engine($this->supabase, $this->privacy_filter);
        }
    }

    /**
     * Register WordPress hooks
     */
    private function register_hooks() {
        // Activation/Deactivation hooks
        register_activation_hook(ASEAGI_WP_PLUGIN_FILE, array($this, 'activate'));
        register_deactivation_hook(ASEAGI_WP_PLUGIN_FILE, array($this, 'deactivate'));

        // Admin hooks
        add_action('admin_menu', array($this, 'register_admin_menu'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_assets'));

        // Custom post types
        add_action('init', array($this, 'register_post_types'));

        // Sync cron job
        add_action('aseagi_sync_cron', array($this, 'run_sync'));

        // Settings
        add_action('admin_init', array($this, 'register_settings'));
    }

    /**
     * Plugin activation
     */
    public function activate() {
        // Register post types for flush_rewrite_rules
        $this->register_post_types();

        // Flush rewrite rules
        flush_rewrite_rules();

        // Schedule cron job (every 15 minutes)
        if (!wp_next_scheduled('aseagi_sync_cron')) {
            wp_schedule_event(time(), 'aseagi_15min', 'aseagi_sync_cron');
        }

        // Create default options
        add_option('aseagi_supabase_url', '');
        add_option('aseagi_supabase_service_key', '');
        add_option('aseagi_sync_enabled', true);
        add_option('aseagi_relevancy_threshold', 700);
        add_option('aseagi_manual_approval_required', true);
        add_option('aseagi_last_sync', 0);
    }

    /**
     * Plugin deactivation
     */
    public function deactivate() {
        // Unschedule cron job
        $timestamp = wp_next_scheduled('aseagi_sync_cron');
        if ($timestamp) {
            wp_unschedule_event($timestamp, 'aseagi_sync_cron');
        }

        // Flush rewrite rules
        flush_rewrite_rules();
    }

    /**
     * Register custom post types
     */
    public function register_post_types() {
        ASEAGI_Timeline_Event_CPT::register();
        ASEAGI_Court_Hearing_CPT::register();
        ASEAGI_Resource_CPT::register();
    }

    /**
     * Register admin menu
     */
    public function register_admin_menu() {
        add_menu_page(
            'ASEAGI Connector',
            'ASEAGI',
            'manage_options',
            'aseagi-connector',
            array($this, 'render_admin_dashboard'),
            'dashicons-shield',
            30
        );

        add_submenu_page(
            'aseagi-connector',
            'Sync Status',
            'Sync Status',
            'manage_options',
            'aseagi-connector',
            array($this, 'render_admin_dashboard')
        );

        add_submenu_page(
            'aseagi-connector',
            'Settings',
            'Settings',
            'manage_options',
            'aseagi-settings',
            array($this, 'render_settings_page')
        );

        add_submenu_page(
            'aseagi-connector',
            'Privacy Filter Logs',
            'Privacy Logs',
            'manage_options',
            'aseagi-privacy-logs',
            array($this, 'render_privacy_logs')
        );
    }

    /**
     * Render admin dashboard
     */
    public function render_admin_dashboard() {
        $dashboard = new ASEAGI_Admin_Dashboard($this->sync_engine);
        $dashboard->render();
    }

    /**
     * Render settings page
     */
    public function render_settings_page() {
        require_once ASEAGI_WP_PLUGIN_DIR . 'includes/admin-settings.php';
    }

    /**
     * Render privacy logs page
     */
    public function render_privacy_logs() {
        require_once ASEAGI_WP_PLUGIN_DIR . 'includes/admin-privacy-logs.php';
    }

    /**
     * Register plugin settings
     */
    public function register_settings() {
        register_setting('aseagi_settings', 'aseagi_supabase_url');
        register_setting('aseagi_settings', 'aseagi_supabase_service_key');
        register_setting('aseagi_settings', 'aseagi_sync_enabled');
        register_setting('aseagi_settings', 'aseagi_relevancy_threshold');
        register_setting('aseagi_settings', 'aseagi_manual_approval_required');
    }

    /**
     * Enqueue admin assets
     */
    public function enqueue_admin_assets($hook) {
        // Only load on ASEAGI admin pages
        if (strpos($hook, 'aseagi') === false) {
            return;
        }

        wp_enqueue_style(
            'aseagi-admin-style',
            ASEAGI_WP_PLUGIN_URL . 'assets/css/admin-style.css',
            array(),
            ASEAGI_WP_VERSION
        );

        wp_enqueue_script(
            'aseagi-admin-script',
            ASEAGI_WP_PLUGIN_URL . 'assets/js/admin-script.js',
            array('jquery'),
            ASEAGI_WP_VERSION,
            true
        );

        // Localize script
        wp_localize_script('aseagi-admin-script', 'aseagiAdmin', array(
            'ajaxUrl' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('aseagi_admin_nonce')
        ));
    }

    /**
     * Run sync (cron job callback)
     */
    public function run_sync() {
        if (!$this->sync_engine) {
            error_log('ASEAGI: Sync engine not initialized');
            return;
        }

        if (!get_option('aseagi_sync_enabled', true)) {
            error_log('ASEAGI: Sync disabled in settings');
            return;
        }

        try {
            $result = $this->sync_engine->sync_all();
            update_option('aseagi_last_sync', time());
            error_log('ASEAGI: Sync completed successfully - ' . json_encode($result));
        } catch (Exception $e) {
            error_log('ASEAGI: Sync failed - ' . $e->getMessage());
        }
    }
}

/**
 * Add custom cron schedule (every 15 minutes)
 */
function aseagi_custom_cron_schedules($schedules) {
    $schedules['aseagi_15min'] = array(
        'interval' => 900, // 15 minutes in seconds
        'display' => __('Every 15 Minutes (ASEAGI)', 'aseagi-wp-connector')
    );
    return $schedules;
}
add_filter('cron_schedules', 'aseagi_custom_cron_schedules');

/**
 * Initialize the plugin
 */
function aseagi_wp_connector_init() {
    return ASEAGI_WP_Connector::get_instance();
}

// Start the plugin
add_action('plugins_loaded', 'aseagi_wp_connector_init');
