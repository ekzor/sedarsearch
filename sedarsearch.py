from datetime import datetime,timedelta
import re
from HTMLParser import HTMLParser
from dateutil import parser, relativedelta

import pytz
import requests
from tabulate import tabulate

from verbosity import Verbosity

class SedarSearch(object):

  params = {}
  _form_url = 'http://www.sedar.com/FindCompanyDocuments.do'
  
  #sort types are based on the radio button choices in the search form; data is not sorted by this script
  _VALID_SORT_TYPES = ['FilingDate','DocType','Issuer']

  def __init__(self,company_name,period_days=7,date_to=datetime.today(),sort_by='FilingDate',verbosity=True):

    self.company_name = company_name
    
    #check if sort type is valid
    if sort_by not in self._VALID_SORT_TYPES:
      raise ValueError('sort_by must be one of the following:',','.join(self._VALID_SORT_TYPES))
    self.sort_by = sort_by
    
    #date can be passed in as either a date object or a string. if it's a string, parse it
    if isinstance(date_to,basestring):
      date_to = parser.parse(date_to)
    self.date_to = date_to
    
    #calculate the date from based on number of days requested 
    self.date_from = self.date_to-timedelta(days=period_days)
    
    self.params = self.construct_params()
    
    self.vlog = Verbosity(verbosity)
    
    self.vlog.print_("Connecting...")
    try:
      r = self.run_query()
    except:
      print "Query failed. Are you connected to the internet?"
      return false
    
    self.vlog.print_("Success! Parsing...")
    #store parsed results
    self.data = self.parse_result(r.text)
    
    
  #dict of search form parameters
  def construct_params(self):
    return {
      'lang':'EN',
      'page_no':'1',
      'company_search':self.company_name,
      'document_selection':'0',
      'industry_group':'A',
      'FromMonth':self.date_from.month,
      'FromDate':self.date_from.day,
      'FromYear':self.date_from.year,
      'ToMonth':self.date_to.month,
      'ToDate':self.date_to.day,
      'ToYear':self.date_to.year,
      'Variable':self.sort_by,
      'Search':'Search'
    }
  
  #submit form request
  def run_query(self):
    r = requests.post(self._form_url,self.params)
    return r
  
  #turn search results into a list of dicts for each result row
  def parse_result(self,result):
    #the filing result table is broken up with <tr class=rt>
    rows = re.findall(r'<TR class=rt>[\s\S]*?</TR>',result)
    #header row is always returned. if there's only 1 row, it's the header; return an empty list
    if len(rows)==1:
      return []
    
    data = []
    
    #if there are results, obtain text data using HTMLParser
    for row in rows[1:]:  
      p = self.SedarRowDataHTMLParser()    
      p.feed(row)
      rowdate = parser.parse(' '.join(p.rowdata[1:3]))
      data.append({
        'company':p.rowdata[0],
        'date':p.rowdata[1],
        'time':p.rowdata[2],
        'title':p.rowdata[3],
        'age':self.timesince(rowdate)
        })
      p.close()
    
    return data
  
  #return age of filing based on current time.
  def timesince(self,rowdate):
  
    #SEDAR provides results in Eastern time. use pytz to convert to UTC, then convert to naive timestamp
    tz = pytz.timezone('US/Eastern')
    rowdate = tz.localize(rowdate).astimezone(pytz.utc).replace(tzinfo=None)
    rd = relativedelta.relativedelta(datetime.today(),rowdate)
    
    #convert the relativedelta object into a string
    attrlist = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    return ' '.join(str(getattr(rd,x))+x[0] for x in attrlist if getattr(rd,x))
    
  #return a simple result table. parameter display_order is column ordering 
  def result_table(self, display_order = ['company','date','time','title','age']):
    display_data = [ [ row[col] for col in display_order ] for row in self.data ]
    return tabulate(display_data,headers=[x[:1].upper()+x[1:] for x in display_order])
  
  def resultpage_url(self):
    return self._form_url+'?'+'&'.join([k+'='+str(v) for k,v in self.params.items()])
  
  #parse a row from the result table using HTMLParser to get just the text contents
  class SedarRowDataHTMLParser(HTMLParser):
  
    #use init to clear the rowdata variable
    def __init__(self):
      self.rowdata = []
      HTMLParser.__init__(self)
    
    #save data from each row
    def handle_data(self,data):
      data = data.strip()
      if len(data) > 0:
        self.rowdata.append(data)
  

if __name__ == '__main__':
  import argparse as ap
  argparser = ap.ArgumentParser()
  argparser.add_argument("company", help="name of the company to be searched",default="test")
  argparser.add_argument("-d", "--days", help="how far back to search (in days)", type=int, default=7)
  argparser.add_argument("-e", "--end", help="what date to search up to (default today)", default='today')
  argparser.add_argument("-s", "--sort", help="criteria to sort the search by", choices=SedarSearch._VALID_SORT_TYPES, default=SedarSearch._VALID_SORT_TYPES[0])
  argparser.add_argument("-w", "--web", help="open the results in your web browser", action="store_true")
  argparser.add_argument("-m", "--mute",  help="hide status messages as the script executes", action="store_true", default=False)
  args = argparser.parse_args()
  
  cf = ConfigParser.ConfigParser()
  
  if args.end == 'today':
    args.end = datetime.today().date().isoformat()
  s = SedarSearch(args.company,args.days,args.end,args.sort,not args.mute)
  
  if args.web:
    import webbrowser
    webbrowser.open(s.resultpage_url())
  else:
    print s.result_table()
    print "Report time: "+datetime.now().strftime('%Y-%m-%d %H:%M:%S')
