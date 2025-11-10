<?php
/**
 * Supabase REST API Client for WordPress
 *
 * Handles all communication with Supabase database using REST API
 *
 * @package ASEAGI_WP_Connector
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

class ASEAGI_Supabase_Client {

    /**
     * @var string Supabase project URL
     */
    private $url;

    /**
     * @var string Supabase service role key
     */
    private $key;

    /**
     * @var string API base URL
     */
    private $api_base;

    /**
     * Constructor
     *
     * @param string $url Supabase project URL
     * @param string $key Supabase service role key
     */
    public function __construct($url, $key) {
        $this->url = rtrim($url, '/');
        $this->key = $key;
        $this->api_base = $this->url . '/rest/v1';
    }

    /**
     * Execute a GET request to Supabase
     *
     * @param string $table Table name
     * @param array $params Query parameters
     * @return array|WP_Error Response data or error
     */
    public function get($table, $params = array()) {
        $url = $this->api_base . '/' . $table;

        // Build query string
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }

        $response = wp_remote_get($url, array(
            'headers' => $this->get_headers(),
            'timeout' => 30
        ));

        return $this->handle_response($response);
    }

    /**
     * Execute a POST request to Supabase
     *
     * @param string $table Table name
     * @param array $data Data to insert
     * @return array|WP_Error Response data or error
     */
    public function post($table, $data) {
        $url = $this->api_base . '/' . $table;

        $response = wp_remote_post($url, array(
            'headers' => $this->get_headers(),
            'body' => json_encode($data),
            'timeout' => 30
        ));

        return $this->handle_response($response);
    }

    /**
     * Execute a PATCH request to Supabase
     *
     * @param string $table Table name
     * @param array $data Data to update
     * @param array $where Where conditions
     * @return array|WP_Error Response data or error
     */
    public function patch($table, $data, $where = array()) {
        $url = $this->api_base . '/' . $table;

        // Build where clause
        if (!empty($where)) {
            $url .= '?' . http_build_query($where);
        }

        $response = wp_remote_request($url, array(
            'method' => 'PATCH',
            'headers' => $this->get_headers(),
            'body' => json_encode($data),
            'timeout' => 30
        ));

        return $this->handle_response($response);
    }

    /**
     * Execute a DELETE request to Supabase
     *
     * @param string $table Table name
     * @param array $where Where conditions
     * @return array|WP_Error Response data or error
     */
    public function delete($table, $where) {
        $url = $this->api_base . '/' . $table;

        // Build where clause
        if (!empty($where)) {
            $url .= '?' . http_build_query($where);
        }

        $response = wp_remote_request($url, array(
            'method' => 'DELETE',
            'headers' => $this->get_headers(),
            'timeout' => 30
        ));

        return $this->handle_response($response);
    }

    /**
     * Get timeline events for public display
     *
     * Fetches court events with relevancy >= threshold
     *
     * @param int $relevancy_threshold Minimum relevancy score
     * @param int $limit Maximum number of records
     * @return array|WP_Error Timeline events or error
     */
    public function get_timeline_events($relevancy_threshold = 700, $limit = 100) {
        $params = array(
            'select' => '*',
            'relevancy_number' => 'gte.' . $relevancy_threshold,
            'order' => 'event_date.desc',
            'limit' => $limit
        );

        return $this->get('court_events', $params);
    }

    /**
     * Get court hearings for calendar display
     *
     * @param string $start_date Start date (YYYY-MM-DD)
     * @param string $end_date End date (YYYY-MM-DD)
     * @return array|WP_Error Court hearings or error
     */
    public function get_court_hearings($start_date = null, $end_date = null) {
        $params = array(
            'select' => '*',
            'order' => 'hearing_date.asc'
        );

        if ($start_date) {
            $params['hearing_date'] = 'gte.' . $start_date;
        }

        if ($end_date) {
            $params['hearing_date'] = 'lte.' . $end_date;
        }

        return $this->get('court_events', $params);
    }

    /**
     * Get high-relevancy legal documents
     *
     * @param int $relevancy_threshold Minimum relevancy score
     * @param int $limit Maximum number of records
     * @return array|WP_Error Documents or error
     */
    public function get_legal_documents($relevancy_threshold = 900, $limit = 50) {
        $params = array(
            'select' => '*',
            'relevancy_number' => 'gte.' . $relevancy_threshold,
            'order' => 'created_at.desc',
            'limit' => $limit
        );

        return $this->get('legal_documents', $params);
    }

    /**
     * Get legal violations for public display
     *
     * @param int $limit Maximum number of records
     * @return array|WP_Error Violations or error
     */
    public function get_legal_violations($limit = 100) {
        $params = array(
            'select' => '*',
            'order' => 'created_at.desc',
            'limit' => $limit
        );

        return $this->get('legal_violations', $params);
    }

    /**
     * Get resources directory entries
     *
     * @param string $type Resource type filter
     * @param int $limit Maximum number of records
     * @return array|WP_Error Resources or error
     */
    public function get_resources($type = null, $limit = 100) {
        $params = array(
            'select' => '*',
            'verified' => 'eq.true',
            'public_safe' => 'eq.true',
            'order' => 'resource_name.asc',
            'limit' => $limit
        );

        if ($type) {
            $params['resource_type'] = 'eq.' . $type;
        }

        return $this->get('resources', $params);
    }

    /**
     * Get case statistics
     *
     * @return array Statistics array
     */
    public function get_statistics() {
        $stats = array(
            'total_documents' => 0,
            'smoking_gun_count' => 0,
            'court_hearings_count' => 0,
            'violations_count' => 0,
            'days_since_removal' => 0
        );

        // Get document count
        $docs = $this->get('legal_documents', array('select' => 'count'));
        if (!is_wp_error($docs) && isset($docs[0]['count'])) {
            $stats['total_documents'] = (int) $docs[0]['count'];
        }

        // Get smoking gun count (relevancy >= 900)
        $smoking_guns = $this->get('legal_documents', array(
            'select' => 'count',
            'relevancy_number' => 'gte.900'
        ));
        if (!is_wp_error($smoking_guns) && isset($smoking_guns[0]['count'])) {
            $stats['smoking_gun_count'] = (int) $smoking_guns[0]['count'];
        }

        // Get court hearings count
        $hearings = $this->get('court_events', array('select' => 'count'));
        if (!is_wp_error($hearings) && isset($hearings[0]['count'])) {
            $stats['court_hearings_count'] = (int) $hearings[0]['count'];
        }

        // Get violations count
        $violations = $this->get('legal_violations', array('select' => 'count'));
        if (!is_wp_error($violations) && isset($violations[0]['count'])) {
            $stats['violations_count'] = (int) $violations[0]['count'];
        }

        return $stats;
    }

    /**
     * Mark document as synced to WordPress
     *
     * @param int $document_id Document ID in Supabase
     * @param int $wp_post_id WordPress post ID
     * @return array|WP_Error Response or error
     */
    public function mark_synced($table, $supabase_id, $wp_post_id) {
        return $this->patch($table, array(
            'synced_to_wordpress' => true,
            'wordpress_post_id' => $wp_post_id
        ), array(
            'id' => 'eq.' . $supabase_id
        ));
    }

    /**
     * Test connection to Supabase
     *
     * @return bool|WP_Error True if connected, error otherwise
     */
    public function test_connection() {
        $response = $this->get('legal_documents', array('limit' => 1));

        if (is_wp_error($response)) {
            return $response;
        }

        return true;
    }

    /**
     * Get request headers for Supabase API
     *
     * @return array Headers
     */
    private function get_headers() {
        return array(
            'Content-Type' => 'application/json',
            'apikey' => $this->key,
            'Authorization' => 'Bearer ' . $this->key
        );
    }

    /**
     * Handle API response
     *
     * @param array|WP_Error $response Response from wp_remote_*
     * @return array|WP_Error Parsed data or error
     */
    private function handle_response($response) {
        if (is_wp_error($response)) {
            return $response;
        }

        $status_code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);

        // Success
        if ($status_code >= 200 && $status_code < 300) {
            $data = json_decode($body, true);

            if (json_last_error() !== JSON_ERROR_NONE) {
                return new WP_Error(
                    'json_decode_error',
                    'Failed to decode JSON response: ' . json_last_error_msg()
                );
            }

            return $data;
        }

        // Error
        $error_data = json_decode($body, true);
        $error_message = isset($error_data['message'])
            ? $error_data['message']
            : 'Supabase API error';

        return new WP_Error(
            'supabase_api_error',
            sprintf('Supabase API Error (%d): %s', $status_code, $error_message),
            array('status' => $status_code, 'body' => $body)
        );
    }
}
