<?php
/**
 * Privacy Filter Engine
 *
 * Protects sensitive information when displaying legal case data publicly
 * Implements comprehensive redaction rules for HIPAA, FERPA, and privacy compliance
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class ASEAGI_Privacy_Filter {

    /**
     * @var array Privacy filter logs
     */
    private $logs = array();

    /**
     * @var array Redaction patterns
     */
    private $patterns = array();

    /**
     * Constructor
     */
    public function __construct() {
        $this->init_patterns();
    }

    /**
     * Initialize redaction patterns
     */
    private function init_patterns() {
        $this->patterns = array(
            // Names (full names with 2+ parts)
            'full_name' => array(
                'pattern' => '/\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b/',
                'replacement' => '[Name Redacted]',
                'description' => 'Full names'
            ),

            // Email addresses
            'email' => array(
                'pattern' => '/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/',
                'replacement' => '[Email Redacted]',
                'description' => 'Email addresses'
            ),

            // Phone numbers (various formats)
            'phone' => array(
                'pattern' => '/\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b/',
                'replacement' => '[Phone Redacted]',
                'description' => 'Phone numbers'
            ),

            // Addresses (street addresses)
            'address' => array(
                'pattern' => '/\b\d+\s+(?:[A-Z][a-z]*\s*){1,4}(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Road|Rd|Lane|Ln|Court|Ct|Way|Place|Pl)\b/i',
                'replacement' => '[Address Redacted]',
                'description' => 'Street addresses'
            ),

            // SSN (Social Security Numbers)
            'ssn' => array(
                'pattern' => '/\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b/',
                'replacement' => '[SSN Redacted]',
                'description' => 'Social Security Numbers'
            ),

            // Case numbers
            'case_number' => array(
                'pattern' => '/\b(?:Case|Docket|File)\s*#?\s*[A-Z0-9]+-[A-Z0-9]+\b/i',
                'replacement' => '[Case # Redacted]',
                'description' => 'Case numbers'
            ),

            // Birth dates
            'birthdate' => array(
                'pattern' => '/\b(?:DOB|Date of Birth|Born on|Birth Date)[\s:]+\d{1,2}\/\d{1,2}\/\d{2,4}\b/i',
                'replacement' => '[DOB Redacted]',
                'description' => 'Dates of birth'
            ),

            // Medical record numbers
            'mrn' => array(
                'pattern' => '/\b(?:MRN|Medical Record|Patient ID)[\s:#]+[A-Z0-9]+\b/i',
                'replacement' => '[Medical Record Redacted]',
                'description' => 'Medical record numbers'
            ),

            // Driver's license
            'drivers_license' => array(
                'pattern' => '/\b(?:DL|Driver\'?s License)[\s:#]+[A-Z0-9]+\b/i',
                'replacement' => '[DL Redacted]',
                'description' => 'Driver\'s license numbers'
            ),

            // Bank account numbers
            'bank_account' => array(
                'pattern' => '/\b(?:Account|Acct)[\s:#]+\d{8,17}\b/i',
                'replacement' => '[Account Redacted]',
                'description' => 'Bank account numbers'
            ),

            // Credit card numbers
            'credit_card' => array(
                'pattern' => '/\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/',
                'replacement' => '[Card Redacted]',
                'description' => 'Credit card numbers'
            )
        );
    }

    /**
     * Filter content for public display
     *
     * @param string $content Content to filter
     * @param string $content_type Type of content (timeline_event, court_hearing, etc.)
     * @param array $metadata Additional metadata for context
     * @return string Filtered content
     */
    public function filter_content($content, $content_type = 'general', $metadata = array()) {
        if (empty($content)) {
            return $content;
        }

        $original_content = $content;
        $redactions_made = array();

        // Apply all redaction patterns
        foreach ($this->patterns as $pattern_name => $pattern_data) {
            $matches_before = preg_match_all($pattern_data['pattern'], $content);
            $content = preg_replace(
                $pattern_data['pattern'],
                $pattern_data['replacement'],
                $content
            );
            $matches_after = preg_match_all($pattern_data['pattern'], $content);

            if ($matches_before > $matches_after) {
                $redactions_made[] = array(
                    'pattern' => $pattern_name,
                    'count' => $matches_before - $matches_after,
                    'description' => $pattern_data['description']
                );
            }
        }

        // Apply custom redactions for specific content types
        if ($content_type === 'timeline_event') {
            $content = $this->filter_timeline_event($content);
        } elseif ($content_type === 'court_hearing') {
            $content = $this->filter_court_hearing($content);
        } elseif ($content_type === 'document_summary') {
            $content = $this->filter_document_summary($content, $metadata);
        }

        // Standardize name references
        $content = $this->standardize_names($content);

        // Log redactions if any were made
        if (!empty($redactions_made)) {
            $this->log_redaction($original_content, $content, $redactions_made, $content_type);
        }

        return $content;
    }

    /**
     * Filter timeline event content
     *
     * @param string $content Event description
     * @return string Filtered content
     */
    private function filter_timeline_event($content) {
        // Remove specific judge names
        $content = preg_replace('/Judge\s+[A-Z][a-z]+\s+[A-Z][a-z]+/', 'Judge [Name Redacted]', $content);

        // Remove opposing counsel names
        $content = preg_replace('/Attorney\s+[A-Z][a-z]+\s+[A-Z][a-z]+/', 'Attorney [Name Redacted]', $content);

        // Generalize locations
        $content = preg_replace('/\b\d+\s+[A-Z][a-z]*\s+(?:St|Ave|Blvd|Dr|Rd)\b/i', '[Location]', $content);

        return $content;
    }

    /**
     * Filter court hearing content
     *
     * @param string $content Hearing description
     * @return string Filtered content
     */
    private function filter_court_hearing($content) {
        // Remove courtroom numbers (sometimes contain judge info)
        $content = preg_replace('/Courtroom\s+\d+/', 'Courtroom [Redacted]', $content);

        // Remove department numbers
        $content = preg_replace('/Department\s+[A-Z0-9]+/', 'Department [Redacted]', $content);

        return $content;
    }

    /**
     * Filter document summary
     *
     * @param string $content Summary text
     * @param array $metadata Document metadata
     * @return string Filtered content
     */
    private function filter_document_summary($content, $metadata = array()) {
        // Only show summaries for high-relevancy documents
        $relevancy = isset($metadata['relevancy']) ? (int) $metadata['relevancy'] : 0;

        if ($relevancy < 700) {
            return ''; // Don't show low-relevancy document summaries
        }

        // For smoking gun evidence (900+), be extra cautious
        if ($relevancy >= 900) {
            // Remove any specific dates that might identify individuals
            $content = preg_replace('/\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/', '[Date]', $content);

            // Remove times
            $content = preg_replace('/\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b/', '[Time]', $content);
        }

        return $content;
    }

    /**
     * Standardize name references to generic terms
     *
     * @param string $content Content to standardize
     * @return string Content with standardized names
     */
    private function standardize_names($content) {
        // This would be customized based on specific case needs
        // For Ashe's case, replace specific names with generic terms

        // Example: Replace mother's name with "Mother"
        // $content = str_replace('Jane Doe', 'Mother', $content);

        // Replace child's name with "Child" or "Ashe"
        // $content = str_replace('Specific Child Name', 'Child', $content);

        // Note: Actual names should be configured in WordPress settings
        $mother_name = get_option('aseagi_mother_name', '');
        $child_name = get_option('aseagi_child_name', '');

        if (!empty($mother_name)) {
            $content = str_replace($mother_name, 'Mother', $content);
        }

        if (!empty($child_name)) {
            $content = str_replace($child_name, 'Ashe', $content);
        }

        return $content;
    }

    /**
     * Check if content is safe for public display
     *
     * @param string $content Content to check
     * @param int $relevancy_score Document relevancy score
     * @return bool True if safe to display
     */
    public function is_public_safe($content, $relevancy_score = 0) {
        // Don't display low-relevancy content
        $threshold = (int) get_option('aseagi_relevancy_threshold', 700);
        if ($relevancy_score < $threshold) {
            return false;
        }

        // Check for remaining sensitive patterns after filtering
        $filtered = $this->filter_content($content);

        // If filtering removed more than 50% of content, it's too sensitive
        $original_length = strlen($content);
        $filtered_length = strlen($filtered);

        if ($filtered_length < ($original_length * 0.5)) {
            $this->log_rejected_content($content, 'Too much content redacted');
            return false;
        }

        // Check for specific red flag keywords
        $red_flags = array(
            'medical diagnosis',
            'therapy session',
            'school record',
            'psychiatric',
            'substance abuse',
            'sexual abuse details',
            'home address',
            'phone number',
            'email address'
        );

        foreach ($red_flags as $flag) {
            if (stripos($filtered, $flag) !== false) {
                $this->log_rejected_content($content, 'Contains red flag: ' . $flag);
                return false;
            }
        }

        return true;
    }

    /**
     * Log redaction activity
     *
     * @param string $original Original content
     * @param string $filtered Filtered content
     * @param array $redactions Redactions made
     * @param string $content_type Content type
     */
    private function log_redaction($original, $filtered, $redactions, $content_type) {
        $log_entry = array(
            'timestamp' => current_time('mysql'),
            'content_type' => $content_type,
            'redactions' => $redactions,
            'original_length' => strlen($original),
            'filtered_length' => strlen($filtered),
            'redaction_percentage' => round((1 - strlen($filtered) / strlen($original)) * 100, 2)
        );

        // Store in WordPress options (limited to last 100 logs)
        $logs = get_option('aseagi_redaction_logs', array());
        array_unshift($logs, $log_entry);
        $logs = array_slice($logs, 0, 100);
        update_option('aseagi_redaction_logs', $logs);

        $this->logs[] = $log_entry;
    }

    /**
     * Log rejected content
     *
     * @param string $content Content that was rejected
     * @param string $reason Reason for rejection
     */
    private function log_rejected_content($content, $reason) {
        $log_entry = array(
            'timestamp' => current_time('mysql'),
            'reason' => $reason,
            'content_preview' => substr($content, 0, 200) . '...'
        );

        $logs = get_option('aseagi_rejected_content_logs', array());
        array_unshift($logs, $log_entry);
        $logs = array_slice($logs, 0, 50);
        update_option('aseagi_rejected_content_logs', $logs);
    }

    /**
     * Get redaction logs
     *
     * @return array Logs
     */
    public function get_logs() {
        return get_option('aseagi_redaction_logs', array());
    }

    /**
     * Get rejected content logs
     *
     * @return array Logs
     */
    public function get_rejected_logs() {
        return get_option('aseagi_rejected_content_logs', array());
    }

    /**
     * Clear logs
     */
    public function clear_logs() {
        delete_option('aseagi_redaction_logs');
        delete_option('aseagi_rejected_content_logs');
        $this->logs = array();
    }

    /**
     * Test filter with sample content
     *
     * @param string $content Sample content
     * @return array Test results
     */
    public function test_filter($content) {
        $filtered = $this->filter_content($content);

        return array(
            'original' => $content,
            'filtered' => $filtered,
            'original_length' => strlen($content),
            'filtered_length' => strlen($filtered),
            'redaction_percentage' => round((1 - strlen($filtered) / strlen($content)) * 100, 2),
            'public_safe' => $this->is_public_safe($content, 800),
            'patterns_detected' => $this->detect_patterns($content)
        );
    }

    /**
     * Detect which patterns are present in content
     *
     * @param string $content Content to check
     * @return array Detected patterns
     */
    private function detect_patterns($content) {
        $detected = array();

        foreach ($this->patterns as $pattern_name => $pattern_data) {
            if (preg_match($pattern_data['pattern'], $content)) {
                $detected[] = array(
                    'name' => $pattern_name,
                    'description' => $pattern_data['description']
                );
            }
        }

        return $detected;
    }
}
