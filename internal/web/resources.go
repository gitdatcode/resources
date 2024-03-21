package web

import (
	"encoding/json"
	"net/http"

	"github.com/gitdatcode/resources/pkg/requests"
)

func (server *Server) resourceSearch(w http.ResponseWriter, r *http.Request) {
	req, err := requests.NewSearchResourcesFromURL(r.URL)
	if err != nil {
		server.HandleError(w, err, "unable to create new search")
		return
	}

	res, err := server.ServiceLayer.ResourceSearch(*req)
	if err != nil {
		server.HandleError(w, err, "unable to create execute search")
		return
	}

	server.RespondJson(res, http.StatusOK, w)
}

func (server *Server) resourceAdd(w http.ResponseWriter, r *http.Request) {
	if r.Body == nil {
		server.HandleError(w, ErrPostBodyRequired, "post body requied")
		return
	}

	decoder := json.NewDecoder(r.Body)
	req := requests.CreateResource{}
	err := decoder.Decode(&req)
	if err != nil {
		server.HandleError(w, err, "cannot create post body")
		return
	}

	res, err := server.ServiceLayer.ResourceAdd(req)
	if err != nil {
		server.HandleError(w, err, "unable to create resource")
		return
	}

	server.RespondJson(res, http.StatusOK, w)
}
