# sedarsearch
this is a command-line app to search SEDAR. it's handy when you want to keep your eye on a company's filings and don't want to have to keep submitting the search form on the SEDAR website (sedar.com). please don't use this application to hammer SEDAR's servers with search requests, as they do not offer a public API. 

this application does **not** download SEDAR filings. it just scrapes and parses search results for display in your console.

## External libraries
* pytz
* requests
* tabulate

## Usage
in:
`> python sedarsearch.py "some company"`

out:
```
Company            Date         Time         Title                             Age
-----------------  -----------  -----------  --------------------------------  --------------
Some Company Inc.  Nov 23 2017  17:55:28 ET  Material change report - English  3d 22h 33m 35s
```

### command-line options:
* -d DAYS, --days DAYS: integer, default: 7. how far back to search from the end date
* -e DATE, --end DATE: iso date, default: today. the endpoint of the search
* -s OPT, --sort OPT: choose one of {FilingDate,DocType,Issuer}, default: FilingDate how to sort the search results. uses SEDAR's search options
* -w, --web: open the search results in your default web browser. this application does not download SEDAR filings, so if you want to click on something, this is a shortcut to the search result page
