<?php

require_once 'google/appengine/api/app_identity/AppIdentityService.php';

use google\appengine\api\app_identity\AppIdentityService;

function projectIDHandler() {
    echo AppIdentityService::getApplicationId();
}

function hostnameHandler() {
    echo AppIdentityService::getDefaultVersionHostname();
}

function accessTokenHandler() {
    $access_token = AppIdentityService::getAccessToken(
        'https://www.googleapis.com/auth/cloud-platform');
    $output = array('token' => $access_token['access_token'],
                    'expires' => $access_token['expiration_time']);
    echo json_encode($output);
}

function signBlobHandler() {
    $encoded_blob = strtr($_GET['blob'], '-_', '+/'); // Convert urlsafe_base64 chars.
    $blob = base64_decode($encoded_blob);
    $signature = AppIdentityService::signForApp($blob);
    $signature['signature'] = base64_encode($signature['signature']);
    echo json_encode($signature);
}

function certificateHandler() {
    $certs = array();
    foreach(AppIdentityService::getPublicCertificates() as $certificate) {
        $certs[] = array('key_name' => $certificate->getCertificateName(),
                         'pem' => $certificate->getX509CertificateInPemFormat());
    }
    echo json_encode($certs);
}

function serviceAccountNameHandler() {
    echo AppIdentityService::getServiceAccountName();
}
