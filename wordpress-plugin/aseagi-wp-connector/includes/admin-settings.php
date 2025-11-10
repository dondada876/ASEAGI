<?php
/**
 * Admin Settings Page
 *
 * Configuration interface for ASEAGI WordPress Connector
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Handle settings save
if (isset($_POST['aseagi_settings_save']) && check_admin_referer('aseagi_settings')) {
    update_option('aseagi_supabase_url', sanitize_text_field($_POST['aseagi_supabase_url']));
    update_option('aseagi_supabase_service_key', sanitize_text_field($_POST['aseagi_supabase_service_key']));
    update_option('aseagi_sync_enabled', isset($_POST['aseagi_sync_enabled']) ? true : false);
    update_option('aseagi_relevancy_threshold', (int)$_POST['aseagi_relevancy_threshold']);
    update_option('aseagi_manual_approval_required', isset($_POST['aseagi_manual_approval_required']) ? true : false);
    update_option('aseagi_mother_name', sanitize_text_field($_POST['aseagi_mother_name']));
    update_option('aseagi_child_name', sanitize_text_field($_POST['aseagi_child_name']));

    echo '<div class="notice notice-success"><p><strong>Settings saved successfully!</strong></p></div>';
}

// Handle connection test
$connection_test_result = null;
if (isset($_POST['test_connection']) && check_admin_referer('aseagi_test_connection')) {
    $supabase_url = get_option('aseagi_supabase_url', '');
    $supabase_key = get_option('aseagi_supabase_service_key', '');

    if (!empty($supabase_url) && !empty($supabase_key)) {
        require_once ASEAGI_WP_PLUGIN_DIR . 'includes/class-supabase-client.php';
        $client = new ASEAGI_Supabase_Client($supabase_url, $supabase_key);
        $test_result = $client->test_connection();

        if (is_wp_error($test_result)) {
            $connection_test_result = array(
                'success' => false,
                'message' => $test_result->get_error_message()
            );
        } else {
            $connection_test_result = array(
                'success' => true,
                'message' => 'Connection successful!'
            );
        }
    } else {
        $connection_test_result = array(
            'success' => false,
            'message' => 'Please enter both Supabase URL and Service Key'
        );
    }
}

// Get current settings
$supabase_url = get_option('aseagi_supabase_url', '');
$supabase_key = get_option('aseagi_supabase_service_key', '');
$sync_enabled = get_option('aseagi_sync_enabled', true);
$relevancy_threshold = get_option('aseagi_relevancy_threshold', 700);
$manual_approval = get_option('aseagi_manual_approval_required', true);
$mother_name = get_option('aseagi_mother_name', '');
$child_name = get_option('aseagi_child_name', '');
?>

<div class="wrap">
    <h1>⚙️ ASEAGI Settings</h1>

    <?php if ($connection_test_result): ?>
        <div class="notice notice-<?php echo $connection_test_result['success'] ? 'success' : 'error'; ?>">
            <p><?php echo esc_html($connection_test_result['message']); ?></p>
        </div>
    <?php endif; ?>

    <form method="post" action="">
        <?php wp_nonce_field('aseagi_settings'); ?>

        <h2>Supabase Connection</h2>
        <p>Connect to your Supabase database to sync legal case data.</p>

        <table class="form-table">
            <tr>
                <th scope="row">
                    <label for="aseagi_supabase_url">Supabase Project URL</label>
                </th>
                <td>
                    <input type="url"
                           id="aseagi_supabase_url"
                           name="aseagi_supabase_url"
                           value="<?php echo esc_attr($supabase_url); ?>"
                           class="regular-text"
                           placeholder="https://your-project.supabase.co"
                           required>
                    <p class="description">Your Supabase project URL (found in project settings)</p>
                </td>
            </tr>
            <tr>
                <th scope="row">
                    <label for="aseagi_supabase_service_key">Supabase Service Key</label>
                </th>
                <td>
                    <input type="password"
                           id="aseagi_supabase_service_key"
                           name="aseagi_supabase_service_key"
                           value="<?php echo esc_attr($supabase_key); ?>"
                           class="large-text"
                           placeholder="eyJ..."
                           required>
                    <p class="description">
                        <strong>⚠️ Use the service_role key, not the anon key.</strong>
                        Found in Supabase → Settings → API. Keep this secret!
                    </p>
                </td>
            </tr>
        </table>

        <h2>Sync Settings</h2>

        <table class="form-table">
            <tr>
                <th scope="row">
                    <label for="aseagi_sync_enabled">Enable Automatic Sync</label>
                </th>
                <td>
                    <label>
                        <input type="checkbox"
                               id="aseagi_sync_enabled"
                               name="aseagi_sync_enabled"
                               value="1"
                               <?php checked($sync_enabled, true); ?>>
                        Sync data from Supabase every 15 minutes
                    </label>
                    <p class="description">Uncheck to disable automatic syncing (you can still manually sync)</p>
                </td>
            </tr>
            <tr>
                <th scope="row">
                    <label for="aseagi_relevancy_threshold">Relevancy Threshold</label>
                </th>
                <td>
                    <input type="number"
                           id="aseagi_relevancy_threshold"
                           name="aseagi_relevancy_threshold"
                           value="<?php echo esc_attr($relevancy_threshold); ?>"
                           min="0"
                           max="1000"
                           class="small-text">
                    <p class="description">
                        Only sync documents with relevancy score >= this value<br>
                        PROJ344 Scale: 900+ smoking gun, 800-899 high, 700-799 important<br>
                        <strong>Recommended: 700</strong>
                    </p>
                </td>
            </tr>
            <tr>
                <th scope="row">
                    <label for="aseagi_manual_approval_required">Manual Approval Required</label>
                </th>
                <td>
                    <label>
                        <input type="checkbox"
                               id="aseagi_manual_approval_required"
                               name="aseagi_manual_approval_required"
                               value="1"
                               <?php checked($manual_approval, true); ?>>
                        Require manual approval before publishing synced content
                    </label>
                    <p class="description">
                        <strong>Recommended: Enabled</strong> for maximum privacy protection<br>
                        Synced posts will be saved as drafts for your review
                    </p>
                </td>
            </tr>
        </table>

        <h2>Privacy Settings</h2>
        <p>Configure name redaction for public display. Leave blank to use generic terms.</p>

        <table class="form-table">
            <tr>
                <th scope="row">
                    <label for="aseagi_mother_name">Mother's Name</label>
                </th>
                <td>
                    <input type="text"
                           id="aseagi_mother_name"
                           name="aseagi_mother_name"
                           value="<?php echo esc_attr($mother_name); ?>"
                           class="regular-text"
                           placeholder="Leave blank to not redact">
                    <p class="description">Will be replaced with "Mother" in all public content</p>
                </td>
            </tr>
            <tr>
                <th scope="row">
                    <label for="aseagi_child_name">Child's Name</label>
                </th>
                <td>
                    <input type="text"
                           id="aseagi_child_name"
                           name="aseagi_child_name"
                           value="<?php echo esc_attr($child_name); ?>"
                           class="regular-text"
                           placeholder="Leave blank to not redact">
                    <p class="description">Will be replaced with "Ashe" in all public content</p>
                </td>
            </tr>
        </table>

        <p class="submit">
            <button type="submit" name="aseagi_settings_save" class="button button-primary button-large">
                💾 Save Settings
            </button>
        </p>
    </form>

    <hr>

    <h2>Test Connection</h2>
    <p>Test your Supabase connection to ensure it's configured correctly.</p>

    <form method="post" action="">
        <?php wp_nonce_field('aseagi_test_connection'); ?>
        <button type="submit" name="test_connection" class="button button-secondary">
            🔌 Test Connection
        </button>
    </form>

    <hr>

    <h2>Documentation</h2>
    <div style="background: #fff; padding: 20px; border-left: 4px solid #0073aa;">
        <h3>Required Supabase Tables</h3>
        <p>Your Supabase database must have these tables for the plugin to work:</p>
        <ul>
            <li><code>legal_documents</code> - Legal documents with relevancy scoring</li>
            <li><code>court_events</code> - Court hearings and timeline events</li>
            <li><code>legal_violations</code> - Legal violations and issues</li>
            <li><code>resources</code> - Community resources and support services</li>
        </ul>

        <h3>Required Fields</h3>
        <p><strong>court_events table:</strong></p>
        <ul>
            <li><code>id</code> (bigint, primary key)</li>
            <li><code>event_title</code> (text)</li>
            <li><code>event_description</code> (text)</li>
            <li><code>event_date</code> (date)</li>
            <li><code>event_type</code> (text)</li>
            <li><code>relevancy_number</code> (integer 0-1000)</li>
            <li><code>synced_to_wordpress</code> (boolean)</li>
            <li><code>wordpress_post_id</code> (integer)</li>
        </ul>

        <p><strong>resources table:</strong></p>
        <ul>
            <li><code>id</code> (bigint, primary key)</li>
            <li><code>resource_name</code> (text)</li>
            <li><code>description</code> (text)</li>
            <li><code>resource_type</code> (text: legal, support, government, community)</li>
            <li><code>contact_info</code> (text)</li>
            <li><code>website_url</code> (text)</li>
            <li><code>verified</code> (boolean)</li>
            <li><code>public_safe</code> (boolean)</li>
            <li><code>relevancy_score</code> (integer 0-1000)</li>
        </ul>

        <h3>Security Notes</h3>
        <ul>
            <li><strong>Never use the anon key</strong> - Always use the service_role key for server-side operations</li>
            <li><strong>Keep your keys secret</strong> - Never commit them to Git or share publicly</li>
            <li><strong>Enable Row Level Security (RLS)</strong> in Supabase for maximum security</li>
            <li><strong>Review all drafted content</strong> before publishing to ensure privacy compliance</li>
        </ul>
    </div>
</div>
<?php
