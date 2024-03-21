package middleware

import "net/http"

type Middleware func(next http.HandlerFunc) http.HandlerFunc

func Chain(handler http.HandlerFunc, middlewares ...Middleware) http.HandlerFunc {
	lenMW := len(middlewares)
	for i := 0; i < lenMW; i++ {
		handler = middlewares[lenMW-i-1](handler)
	}

	return handler
}
