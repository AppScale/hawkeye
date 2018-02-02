<?php

require 'app_identity.php';

$request_uri = $_SERVER['PATH_INFO'];

$routes = array(
    '/php/app_identity/project_id' => 'projectIDHandler',
    '/php/app_identity/hostname' => 'hostnameHandler',
    '/php/app_identity/access_token' => 'accessTokenHandler',
    '/php/app_identity/sign' => 'signBlobHandler',
    '/php/app_identity/certificates' => 'certificateHandler',
    '/php/app_identity/service_account_name' => 'serviceAccountNameHandler'
);

if (array_key_exists($request_uri, $routes)) {
    call_user_func($routes[$request_uri]);
} else {
    header('HTTP/1.0 404 Not Found');
    echo "Not Found";
}
