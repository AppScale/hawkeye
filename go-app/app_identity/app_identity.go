package app_identity

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net/http"

	"appengine"
)

type AccessToken struct {
	Token   string `json:"token"`
	Expires int64  `json:"expires"`
}

type Certificate struct {
	KeyName string `json:"key_name"`
	PEM     string `json:"pem"`
}

type Signature struct {
	KeyName   string `json:"key_name"`
	Signature string `json:"signature"`
}

func ProjectIDHandler(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	fmt.Fprint(w, appengine.AppID(c))
}

func HostnameHandler(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	fmt.Fprint(w, appengine.DefaultVersionHostname(c))
}

func AccessTokenHandler(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)

	token, expirationTime, err := appengine.AccessToken(
		c, "https://www.googleapis.com/auth/cloud-platform")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	accessToken := AccessToken{token, expirationTime.Unix()}
	output, err := json.Marshal(accessToken)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprint(w, string(output))
}

func SignBlobHandler(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)

	encodedBlob := r.FormValue("blob")
	blob, err := base64.URLEncoding.DecodeString(encodedBlob)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	keyName, signature, err := appengine.SignBytes(c, blob)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	encodedSignature := base64.StdEncoding.EncodeToString(signature)
	signatureStruct := Signature{keyName, encodedSignature}
	output, err := json.Marshal(signatureStruct)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprint(w, string(output))
}

func CertificateHandler(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)

	certificates, err := appengine.PublicCertificates(c)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	certificateStructs := []Certificate{}
	for _, certificate := range certificates {
		certificateStruct := Certificate{
			certificate.KeyName, string(certificate.Data)}
		certificateStructs = append(certificateStructs, certificateStruct)
	}

	output, err := json.Marshal(certificateStructs)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fmt.Fprint(w, string(output))
}

func ServiceAccountNameHandler(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	serviceAccountName, err := appengine.ServiceAccount(c)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	fmt.Fprint(w, serviceAccountName)
}
