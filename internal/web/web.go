package web

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"

	"github.com/gitdatcode/resources/internal/service"
	"github.com/gitdatcode/resources/pkg/requests"
)

var (
	ErrPostBodyRequired = errors.New("request body required")
)

func New(serviceLayer *service.Resources, port string) *Web {

	mux := http.NewServeMux()
	web := &Web{
		Router:       mux,
		ServiceLayer: serviceLayer,
		port:         port,
	}

	web.DefineRoutes()

	return web
}

type Web struct {
	Router       *http.ServeMux
	ServiceLayer *service.Resources
	port         string
}

func (web *Web) Start() error {
	log.Printf(`web started %v`, web.port)
	err := http.ListenAndServe(web.port, web.Router)
	if err != nil {
		return err
	}

	return nil
}

func (web *Web) DefineRoutes() {
	web.Router.HandleFunc("GET /search", web.search)
	web.Router.HandleFunc("POST /resource", web.addResource)
}

func (web *Web) RespondJson(content any, status int, w http.ResponseWriter) {
	resp, err := json.Marshal(content)
	if err != nil {
		web.HandleError(w, err, "unable to handle json conversion")
		return
	}

	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(status)
	if _, err = w.Write(resp); err != nil {
		web.HandleError(w, err, "unable to write response")
		return
	}
}

func (web *Web) HandleError(w http.ResponseWriter, err error, message string) {
	log.Printf(`error during http call -- %v`, err)

}

func (web *Web) search(w http.ResponseWriter, r *http.Request) {
	req, err := requests.NewSearchResourcesFromURL(r.URL)
	if err != nil {
		web.HandleError(w, err, "unable to create new search")
		return
	}

	res, err := web.ServiceLayer.ResourceSearch(*req)
	if err != nil {
		web.HandleError(w, err, "unable to create execute search")
		return
	}

	web.RespondJson(res, http.StatusOK, w)
}

func (web *Web) addResource(w http.ResponseWriter, r *http.Request) {
	if r.Body == nil {
		web.HandleError(w, ErrPostBodyRequired, "post body requied")
		return
	}

	decoder := json.NewDecoder(r.Body)
	req := requests.CreateResource{}
	err := decoder.Decode(&req)
	if err != nil {
		web.HandleError(w, err, "cannot create post body")
		return
	}

	res, err := web.ServiceLayer.ResourceAdd(req)
	if err != nil {
		web.HandleError(w, err, "unable to create resource")
		return
	}

	web.RespondJson(res, http.StatusOK, w)
}
