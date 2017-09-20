package main

import (
	"net/http"
	"net/url"
	"os"
	"time"

	log "github.com/Sirupsen/logrus"

	"github.com/codegangsta/cli"
	ays "github.com/zero-os/0-orchestrator/api/ays-client"
	"github.com/zero-os/0-orchestrator/api/goraml"
	"github.com/zero-os/0-orchestrator/api/router"
	"github.com/zero-os/0-orchestrator/api/tools"

	"fmt"

	"gopkg.in/validator.v2"
)

func main() {
	var (
		debugLogging  bool
		bindAddr      string
		aysURL        string
		aysRepo       string
		organization  string
		applicationID string
		secret        string
	)
	app := cli.NewApp()
	app.Version = "0.2.0"
	app.Name = "G8OS Stateless GRID API"

	app.Flags = []cli.Flag{
		cli.BoolFlag{
			Name:        "debug, d",
			Usage:       "Enable debug logging",
			Destination: &debugLogging,
		},
		cli.StringFlag{
			Name:        "bind, b",
			Usage:       "Bind address",
			Value:       ":5000",
			Destination: &bindAddr,
		},
		cli.StringFlag{
			Name:        "ays-url",
			Usage:       "URL of the AYS API",
			Destination: &aysURL,
		},
		cli.StringFlag{
			Name:        "ays-repo",
			Value:       "objstor",
			Usage:       "AYS repository name",
			Destination: &aysRepo,
		},
		cli.StringFlag{
			Name:        "org",
			Usage:       "Itsyouonline organization to authenticate against",
			Destination: &organization,
		},
		cli.StringFlag{
			Name:        "application-id",
			Usage:       "Itsyouonline applicationID",
			Destination: &applicationID,
		},
		cli.StringFlag{
			Name:        "secret",
			Usage:       "Itsyouonline secret",
			Destination: &secret,
		},
	}

	app.Before = func(c *cli.Context) error {
		if debugLogging {
			log.SetLevel(log.DebugLevel)
			log.Debug("Debug logging enabled")
		}

		var err error
		for err = testAYSURL(aysURL); err != nil; err = testAYSURL(aysURL) {
			log.Error(err)
			time.Sleep(time.Second)
		}

		if err := ensureAYSRepo(aysURL, aysRepo); err != nil {
			log.Fatalln(err.Error())
		}

		if organization != "" {
			if _, err := tools.RefreshToken(applicationID, secret, organization); err != nil {
				log.Fatalln(err.Error())
			}
		}

		return nil
	}

	app.Action = func(c *cli.Context) {
		validator.SetValidationFunc("multipleOf", goraml.MultipleOf)
		r := router.GetRouter(aysURL, aysRepo, organization, applicationID, secret)

		log.Println("starting server")
		log.Printf("Server is listening on %s\n", bindAddr)
		if err := http.ListenAndServe(bindAddr, r); err != nil {
			log.Errorln(err)
		}
	}

	app.Run(os.Args)
}

func testAYSURL(aysURL string) error {
	if aysURL == "" {
		return fmt.Errorf("AYS URL is not specified")
	}
	u, err := url.Parse(aysURL)
	if err != nil {
		return fmt.Errorf("format of the AYS URL is not valid: %v", err)
	}

	resp, err := http.Get(u.String())
	if err != nil {
		return fmt.Errorf("AYS API is not reachable : %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("AYS API is not reachable")
	}

	return nil
}

//ensureAYSRepo make sure that the AYS repository we are going to use exists
func ensureAYSRepo(url, name string) error {
	aysAPI := ays.NewAtYourServiceAPI()
	aysAPI.BaseURI = url
	_, resp, _ := aysAPI.Ays.GetRepository(name, map[string]interface{}{}, map[string]interface{}{})
	if resp.StatusCode == http.StatusNotFound {

		req := ays.AysRepositoryPostReqBody{
			Name:    name,
			Git_url: "http://github.com/fake/fake",
		}
		_, resp, err := aysAPI.Ays.CreateRepository(req, map[string]interface{}{}, map[string]interface{}{})
		if err != nil || resp.StatusCode != http.StatusCreated {
			return fmt.Errorf("Can't create AYS Repo %s :%v", name, err)
		}
	}
	return nil
}
