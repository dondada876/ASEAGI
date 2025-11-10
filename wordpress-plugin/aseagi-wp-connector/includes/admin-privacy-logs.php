<?php
/**
 * Admin Privacy Logs Page
 *
 * Displays redaction logs and rejected content for audit purposes
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Handle log clearing
if (isset($_POST['clear_logs']) && check_admin_referer('aseagi_clear_logs')) {
    delete_option('aseagi_redaction_logs');
    delete_option('aseagi_rejected_content_logs');
    echo '<div class="notice notice-success"><p><strong>Privacy logs cleared successfully!</strong></p></div>';
}

// Get logs
$redaction_logs = get_option('aseagi_redaction_logs', array());
$rejected_logs = get_option('aseagi_rejected_content_logs', array());
?>

<div class="wrap">
    <h1>🔒 Privacy & Redaction Logs</h1>

    <p>
        This page shows all privacy filtering activity to ensure sensitive information is being properly protected.
        Logs are kept for the last 100 redactions and 50 rejected items.
    </p>

    <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
        <h3 style="margin-top: 0;">Privacy Protection Status</h3>
        <p><strong>✓ Privacy Filter: Active</strong></p>
        <p>All content is automatically scanned for:</p>
        <ul style="margin-bottom: 0;">
            <li>Names, addresses, phone numbers, emails</li>
            <li>SSN, case numbers, medical records</li>
            <li>Specific dates, times, and locations that could identify individuals</li>
            <li>Red flag keywords (therapy sessions, medical diagnoses, etc.)</li>
        </ul>
    </div>

    <!-- Statistics -->
    <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
        <h2>Statistics</h2>
        <table class="form-table">
            <tr>
                <th style="width: 250px;">Total Redactions Logged</th>
                <td><strong><?php echo count($redaction_logs); ?></strong></td>
            </tr>
            <tr>
                <th>Total Content Rejected</th>
                <td><strong><?php echo count($rejected_logs); ?></strong></td>
            </tr>
            <tr>
                <th>Average Redaction Percentage</th>
                <td>
                    <?php
                    if (!empty($redaction_logs)) {
                        $total_percentage = 0;
                        foreach ($redaction_logs as $log) {
                            $total_percentage += $log['redaction_percentage'];
                        }
                        $avg = $total_percentage / count($redaction_logs);
                        echo '<strong>' . number_format($avg, 1) . '%</strong>';
                    } else {
                        echo 'N/A';
                    }
                    ?>
                </td>
            </tr>
        </table>
    </div>

    <!-- Redaction Logs -->
    <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
        <h2>Recent Redactions</h2>
        <?php if (empty($redaction_logs)): ?>
            <p>No redaction logs yet. Logs will appear here after the first sync.</p>
        <?php else: ?>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th style="width: 150px;">Timestamp</th>
                        <th>Content Type</th>
                        <th style="width: 100px;">Original Length</th>
                        <th style="width: 100px;">Filtered Length</th>
                        <th style="width: 100px;">Redacted</th>
                        <th>Redaction Types</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach (array_slice($redaction_logs, 0, 50) as $log): ?>
                        <tr>
                            <td><?php echo esc_html($log['timestamp']); ?></td>
                            <td><?php echo esc_html($log['content_type']); ?></td>
                            <td><?php echo number_format($log['original_length']); ?> chars</td>
                            <td><?php echo number_format($log['filtered_length']); ?> chars</td>
                            <td>
                                <strong style="color: <?php echo $log['redaction_percentage'] > 50 ? '#e74c3c' : '#f39c12'; ?>">
                                    <?php echo number_format($log['redaction_percentage'], 1); ?>%
                                </strong>
                            </td>
                            <td>
                                <?php
                                if (!empty($log['redactions'])) {
                                    $types = array();
                                    foreach ($log['redactions'] as $redaction) {
                                        $types[] = $redaction['description'] . ' (' . $redaction['count'] . ')';
                                    }
                                    echo esc_html(implode(', ', $types));
                                }
                                ?>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>

    <!-- Rejected Content -->
    <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
        <h2>Rejected Content</h2>
        <p>Content that was rejected for public display due to privacy concerns.</p>
        <?php if (empty($rejected_logs)): ?>
            <p>No rejected content yet.</p>
        <?php else: ?>
            <table class="wp-list-table widefat fixed striped">
                <thead>
                    <tr>
                        <th style="width: 150px;">Timestamp</th>
                        <th>Reason</th>
                        <th>Content Preview</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach (array_slice($rejected_logs, 0, 50) as $log): ?>
                        <tr>
                            <td><?php echo esc_html($log['timestamp']); ?></td>
                            <td><strong><?php echo esc_html($log['reason']); ?></strong></td>
                            <td>
                                <code style="font-size: 11px; color: #666;">
                                    <?php echo esc_html($log['content_preview']); ?>
                                </code>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>

    <!-- Pattern Detection Details -->
    <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
        <h2>Privacy Filter Patterns</h2>
        <p>The following patterns are automatically detected and redacted:</p>
        <table class="wp-list-table widefat">
            <thead>
                <tr>
                    <th>Pattern Type</th>
                    <th>Description</th>
                    <th>Replacement</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Full Names</strong></td>
                    <td>Names with 2+ parts (e.g., "John Doe")</td>
                    <td><code>[Name Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Email Addresses</strong></td>
                    <td>Any email address format</td>
                    <td><code>[Email Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Phone Numbers</strong></td>
                    <td>Various phone formats (xxx-xxx-xxxx, etc.)</td>
                    <td><code>[Phone Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Street Addresses</strong></td>
                    <td>Numbers + street names (e.g., "123 Main St")</td>
                    <td><code>[Address Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>SSN</strong></td>
                    <td>Social Security Numbers (xxx-xx-xxxx)</td>
                    <td><code>[SSN Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Case Numbers</strong></td>
                    <td>Case/Docket/File numbers</td>
                    <td><code>[Case # Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Dates of Birth</strong></td>
                    <td>DOB, Date of Birth mentions</td>
                    <td><code>[DOB Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Medical Records</strong></td>
                    <td>MRN, Medical Record numbers</td>
                    <td><code>[Medical Record Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Driver's License</strong></td>
                    <td>DL, Driver's License numbers</td>
                    <td><code>[DL Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Bank Accounts</strong></td>
                    <td>Account numbers</td>
                    <td><code>[Account Redacted]</code></td>
                </tr>
                <tr>
                    <td><strong>Credit Cards</strong></td>
                    <td>Credit card numbers</td>
                    <td><code>[Card Redacted]</code></td>
                </tr>
            </tbody>
        </table>
    </div>

    <!-- Actions -->
    <div style="background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin: 20px 0;">
        <h2>Actions</h2>
        <form method="post" action="" onsubmit="return confirm('Are you sure you want to clear all privacy logs? This cannot be undone.');">
            <?php wp_nonce_field('aseagi_clear_logs'); ?>
            <button type="submit" name="clear_logs" class="button button-secondary">
                🗑️ Clear All Logs
            </button>
            <p class="description">Clear all redaction and rejected content logs. This does not affect published content.</p>
        </form>
    </div>

    <!-- Compliance Notes -->
    <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0;">
        <h3 style="margin-top: 0;">Compliance Notes</h3>
        <p><strong>HIPAA Compliance:</strong> Medical information, PHI, and health records are automatically filtered.</p>
        <p><strong>FERPA Compliance:</strong> Educational records and school information are redacted.</p>
        <p><strong>Privacy Best Practices:</strong> All content undergoes automatic privacy filtering before being considered for public display.</p>
        <p style="margin-bottom: 0;"><strong>Manual Review:</strong> Always review drafted content manually before publishing, especially for high-sensitivity cases.</p>
    </div>
</div>
<?php
