package env

import (
	"fmt"
	"log"
	"os"
	"strconv"
)

func Get(key, defaultValue string) string {
	val := os.Getenv(key)
	if val == "" {
		val = defaultValue
	}

	return val
}

func Int(key string, defaultValue int) int {
	val := os.Getenv(key)
	ret, err := strconv.Atoi(val)
	if val == "" || err != nil {
		log.Printf(`unable to convert %v to int -- %v`, key, err)
		ret = defaultValue
	}

	return ret
}

func Required(key string) string {
	val := os.Getenv(key)
	if val == "" {
		msg := fmt.Sprintf(`environment varible "%s" is not defined`, key)
		panic(msg)
	}

	return val
}
