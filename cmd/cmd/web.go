package cmd

import (
	"github.com/spf13/cobra"

	"github.com/gitdatcode/resources/internal/web"
)

func init() {
	var (
		port string
	)

	var server = &cobra.Command{
		Use:   "web",
		Short: "starts the web server",
		Run: func(cmd *cobra.Command, args []string) {
			web := web.New(serviceLayer, port)
			web.Start()
		},
	}

	server.PersistentFlags().StringVar(&port, "port", ":7744", "the port for the http to be served on")

	RootCmd.AddCommand(server)
}
