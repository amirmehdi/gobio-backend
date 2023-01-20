```shell
export $(grep -v '^#' .env | xargs)
```