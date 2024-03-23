package web

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"

	"github.com/gitdatcode/resources/internal/service"
	"github.com/gitdatcode/resources/internal/web/middleware"
)

var (
	ErrPostBodyRequired = errors.New("request body required")
)

func New(serviceLayer *service.Resources, port, slackToken string) *Server {

	mux := http.NewServeMux()
	server := &Server{
		Router:       mux,
		ServiceLayer: serviceLayer,
		port:         port,
		slackToken:   slackToken,
	}

	server.DefineRoutes()

	return server
}

type Server struct {
	Router       *http.ServeMux
	ServiceLayer *service.Resources
	port         string
	slackToken   string
}

func (server *Server) Start() error {
	log.Printf(`web started %v`, server.port)
	err := http.ListenAndServe(server.port, server.Router)
	if err != nil {
		return err
	}

	return nil
}

func (server *Server) DefineRoutes() {
	// server.Router.HandleFunc("GET /search", server.resourceSearch)
	// server.Router.HandleFunc("POST /resource", server.resourceAdd)
	server.Router.HandleFunc("POST /do.bot/command", middleware.Chain(
		server.doBotCommnad,
		middleware.ValidSlackRequest(server.slackToken),
	))
	server.Router.HandleFunc("POST /do.bot/action", middleware.Chain(
		server.doBotAction,
		middleware.ValidSlackRequest(server.slackToken),
	))
}

func (server *Server) RespondJson(content any, status int, w http.ResponseWriter) {
	resp, err := json.Marshal(content)
	if err != nil {
		server.HandleError(w, err, "unable to handle json conversion")
		return
	}

	w.Header().Add("Content-Type", "application/json")
	w.WriteHeader(status)
	if _, err = w.Write(resp); err != nil {
		server.HandleError(w, err, "unable to write response")
		return
	}
}

func (server *Server) HandleError(w http.ResponseWriter, err error, message string) {
	log.Printf(`error during http call -- %v`, err)

}
