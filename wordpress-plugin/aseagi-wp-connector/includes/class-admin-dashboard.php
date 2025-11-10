<?php
/**
 * Admin Dashboard
 *
 * Displays sync status, statistics, and monitoring for ASEAGI WordPress Connector
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class ASEAGI_Admin_Dashboard {

    /**
     * @var ASEAGI_Sync_Engine Sync engine instance
     */
    private $sync_engine;

    /**
     * Constructor
     *
     * @param ASEAGI_Sync_Engine $sync_engine Sync engine
     */
    public function __construct($sync_engine = null) {
        $this->sync_engine = $sync_engine;
    }

    /**
     * Render dashboard page
     */
    public function render() {
        // Handle manual sync request
        if (isset($_POST['manual_sync']) && check_admin_referer('aseagi_manual_sync')) {
            if ($this->sync_engine) {
                $results = $this->sync_engine->manual_sync();
                echo '<div class="notice notice-success"><p><strong>Sync Complete!</strong> ' .
                     'Timeline Events: ' . $results['timeline_events']['synced'] . ' synced, ' .
                     'Court Hearings: ' . $results['court_hearings']['synced'] . ' synced, ' .
                     'Resources: ' . $results['resources']['synced'] . ' synced</p></div>';
            }
        }

        // Get sync stats
        $stats = $this->sync_engine ? $this->sync_engine->get_sync_stats() : array();
        $last_sync = $stats['last_sync'] ?? 0;
        $last_results = $stats['last_results'] ?? array();
        $pending_count = $stats['pending_approval_count'] ?? 0;
        $total_synced = $stats['total_synced'] ?? 0;

        // Get Supabase connection status
        $supabase_url = get_option('aseagi_supabase_url', '');
        $supabase_key = get_option('aseagi_supabase_service_key', '');
        $connected = !empty($supabase_url) && !empty($supabase_key);

        ?>
        <div class="wrap">
            <h1>
                🛡️ ASEAGI WordPress Connector
                <span style="font-size: 14px; font-weight: normal; color: #666;">
                    For Ashe. For Justice. For All Children.
                </span>
            </h1>

            <?php if (!$connected): ?>
            <div class="notice notice-warning">
                <p><strong>⚠️ Supabase Not Connected</strong></p>
                <p>Please configure your Supabase connection in <a href="<?php echo admin_url('admin.php?page=aseagi-settings'); ?>">Settings</a>.</p>
            </div>
            <?php endif; ?>

            <div class="aseagi-dashboard">

                <!-- Statistics Cards -->
                <div class="aseagi-stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">

                    <div class="aseagi-stat-card" style="background: #fff; border-left: 4px solid #0073aa; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Total Synced Posts</h3>
                        <p style="margin: 0; font-size: 36px; font-weight: bold; color: #0073aa;"><?php echo $total_synced; ?></p>
                    </div>

                    <div class="aseagi-stat-card" style="background: #fff; border-left: 4px solid #f39c12; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Pending Approval</h3>
                        <p style="margin: 0; font-size: 36px; font-weight: bold; color: #f39c12;"><?php echo $pending_count; ?></p>
                        <?php if ($pending_count > 0): ?>
                        <a href="<?php echo admin_url('edit.php?post_status=draft&post_type=timeline_event'); ?>" style="font-size: 12px;">Review Now →</a>
                        <?php endif; ?>
                    </div>

                    <div class="aseagi-stat-card" style="background: #fff; border-left: 4px solid #27ae60; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Supabase Status</h3>
                        <p style="margin: 0; font-size: 18px; font-weight: bold;">
                            <?php if ($connected): ?>
                                <span style="color: #27ae60;">✓ Connected</span>
                            <?php else: ?>
                                <span style="color: #e74c3c;">✗ Not Connected</span>
                            <?php endif; ?>
                        </p>
                    </div>

                    <div class="aseagi-stat-card" style="background: #fff; border-left: 4px solid #9b59b6; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <h3 style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Last Sync</h3>
                        <p style="margin: 0; font-size: 14px; font-weight: bold;">
                            <?php if ($last_sync): ?>
                                <?php echo human_time_diff($last_sync, current_time('timestamp')) . ' ago'; ?>
                            <?php else: ?>
                                Never
                            <?php endif; ?>
                        </p>
                    </div>

                </div>

                <!-- Manual Sync Button -->
                <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
                    <h2>Manual Sync</h2>
                    <p>Trigger an immediate sync from Supabase. Normally syncs run automatically every 15 minutes.</p>
                    <form method="post" action="">
                        <?php wp_nonce_field('aseagi_manual_sync'); ?>
                        <button type="submit" name="manual_sync" class="button button-primary button-large">
                            🔄 Sync Now
                        </button>
                        <span style="margin-left: 10px; color: #666;">
                            Next auto-sync: <?php echo $this->get_next_cron_time(); ?>
                        </span>
                    </form>
                </div>

                <!-- Last Sync Results -->
                <?php if (!empty($last_results)): ?>
                <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
                    <h2>Last Sync Results</h2>
                    <table class="wp-list-table widefat fixed striped">
                        <thead>
                            <tr>
                                <th>Content Type</th>
                                <th>Synced</th>
                                <th>Skipped</th>
                                <th>Errors</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Timeline Events</strong></td>
                                <td><?php echo $last_results['timeline_events']['synced'] ?? 0; ?></td>
                                <td><?php echo $last_results['timeline_events']['skipped'] ?? 0; ?></td>
                                <td><?php echo $last_results['timeline_events']['errors'] ?? 0; ?></td>
                            </tr>
                            <tr>
                                <td><strong>Court Hearings</strong></td>
                                <td><?php echo $last_results['court_hearings']['synced'] ?? 0; ?></td>
                                <td><?php echo $last_results['court_hearings']['skipped'] ?? 0; ?></td>
                                <td><?php echo $last_results['court_hearings']['errors'] ?? 0; ?></td>
                            </tr>
                            <tr>
                                <td><strong>Resources</strong></td>
                                <td><?php echo $last_results['resources']['synced'] ?? 0; ?></td>
                                <td><?php echo $last_results['resources']['skipped'] ?? 0; ?></td>
                                <td><?php echo $last_results['resources']['errors'] ?? 0; ?></td>
                            </tr>
                        </tbody>
                    </table>
                    <p style="margin-top: 10px; color: #666;">
                        <strong>Sync Duration:</strong>
                        <?php
                        if (!empty($last_results['start_time']) && !empty($last_results['end_time'])) {
                            $start = strtotime($last_results['start_time']);
                            $end = strtotime($last_results['end_time']);
                            echo ($end - $start) . ' seconds';
                        }
                        ?>
                    </p>
                </div>
                <?php endif; ?>

                <!-- Quick Links -->
                <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
                    <h2>Quick Links</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                        <a href="<?php echo admin_url('edit.php?post_type=timeline_event'); ?>" class="button">
                            📅 Timeline Events
                        </a>
                        <a href="<?php echo admin_url('edit.php?post_type=court_hearing'); ?>" class="button">
                            ⚖️ Court Hearings
                        </a>
                        <a href="<?php echo admin_url('edit.php?post_type=resource'); ?>" class="button">
                            📚 Resources
                        </a>
                        <a href="<?php echo admin_url('admin.php?page=aseagi-settings'); ?>" class="button">
                            ⚙️ Settings
                        </a>
                        <a href="<?php echo admin_url('admin.php?page=aseagi-privacy-logs'); ?>" class="button">
                            🔒 Privacy Logs
                        </a>
                    </div>
                </div>

                <!-- System Information -->
                <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
                    <h2>System Information</h2>
                    <table class="form-table">
                        <tr>
                            <th>Plugin Version</th>
                            <td><?php echo ASEAGI_WP_VERSION; ?></td>
                        </tr>
                        <tr>
                            <th>WordPress Version</th>
                            <td><?php echo get_bloginfo('version'); ?></td>
                        </tr>
                        <tr>
                            <th>PHP Version</th>
                            <td><?php echo PHP_VERSION; ?></td>
                        </tr>
                        <tr>
                            <th>Supabase URL</th>
                            <td><?php echo $supabase_url ? esc_html($supabase_url) : 'Not configured'; ?></td>
                        </tr>
                        <tr>
                            <th>Sync Enabled</th>
                            <td><?php echo get_option('aseagi_sync_enabled', true) ? 'Yes' : 'No'; ?></td>
                        </tr>
                        <tr>
                            <th>Manual Approval Required</th>
                            <td><?php echo get_option('aseagi_manual_approval_required', true) ? 'Yes' : 'No'; ?></td>
                        </tr>
                        <tr>
                            <th>Relevancy Threshold</th>
                            <td><?php echo get_option('aseagi_relevancy_threshold', 700); ?></td>
                        </tr>
                        <tr>
                            <th>Cool Timeline Pro</th>
                            <td><?php echo class_exists('Cool_Timeline') ? '✓ Active' : '✗ Not Installed'; ?></td>
                        </tr>
                        <tr>
                            <th>EventON</th>
                            <td><?php echo class_exists('EventON') ? '✓ Active' : '✗ Not Installed'; ?></td>
                        </tr>
                        <tr>
                            <th>ListingPro</th>
                            <td><?php echo function_exists('listingpro_init') ? '✓ Active' : '✗ Not Installed'; ?></td>
                        </tr>
                    </table>
                </div>

            </div>
        </div>

        <style>
            .aseagi-dashboard h2 {
                margin-top: 0;
                font-size: 18px;
            }
            .aseagi-dashboard .button {
                height: auto;
                padding: 15px 20px;
                text-align: center;
                white-space: normal;
                line-height: 1.4;
            }
        </style>
        <?php
    }

    /**
     * Get next scheduled cron time
     *
     * @return string Human-readable time
     */
    private function get_next_cron_time() {
        $next_run = wp_next_scheduled('aseagi_sync_cron');

        if ($next_run) {
            return human_time_diff($next_run, current_time('timestamp')) . ' from now';
        }

        return 'Not scheduled';
    }
}
