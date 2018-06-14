package app

import (
	"app_identity"
	"net/http"
)

func init() {
	http.HandleFunc("/go/app_identity/project_id", app_identity.ProjectIDHandler)
	http.HandleFunc("/go/app_identity/hostname", app_identity.HostnameHandler)
	http.HandleFunc("/go/app_identity/access_token", app_identity.AccessTokenHandler)
	http.HandleFunc("/go/app_identity/sign", app_identity.SignBlobHandler)
	http.HandleFunc("/go/app_identity/certificates", app_identity.CertificateHandler)
	http.HandleFunc("/go/app_identity/service_account_name", app_identity.ServiceAccountNameHandler)
}
