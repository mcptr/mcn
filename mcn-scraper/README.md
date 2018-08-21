# Mechanoia: scraper

Packages:
```
apt-get install python3-dev libxml2 libxml2-dev libxslt1-dev
```



## mongodb setup


```
use mcn;
db.createUser({
	user: "mcn",
	pwd: "mcn",
	roles: [
		{
			db: "mcn",
			role: "readWrite",
		}
	],
	customData: {},
})
```


## Running workers


Downloading headers (HEAD request):

```
python mcn/scraper/workers/download/head.py
```

Downloading (and caching documents):

```
python mcn/scraper/workers/download/document.py
```
