#!/usr/bin/python
import urllib2, sys, progressbar

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        result.status = code
        return result

def sustained_transfer(theURL, filesize):
   so_far = 0
   counter = 0
   complete = False
   widgets = ['Download: ', progressbar.Percentage(), ' ', 
      progressbar.Bar(marker=progressbar.RotatingMarker()), 
      ' ', progressbar.ETA(), ' ', progressbar.FileTransferSpeed()]
   bar = progressbar.ProgressBar(maxval=filesize, widgets=widgets)
   while not complete:
      # Outer loop - begin new connection
      counter += 1
      filename = "part.%03d" % counter
      print ""
      print "STATUS: Starting:", filename
      outfile = open(filename, "wb")
      resumeURL = (theURL + "?start=%s&end=%s&s=1") % (so_far, filesize)
      print "STATUS: Resuming at:", resumeURL
      response = urllib2.urlopen(resumeURL)
      mid_count = 0
      if (counter == 1):
         bar.start()
      while True:
         try:
            chunk = response.read(1024)
         except:
            chunk = b''
         mid_count += 1
         if not chunk:
            break
         # Otherwise, we have a chunk, let's write it to the current part
         outfile.write(chunk)
         so_far += len(chunk)
         if (not (mid_count % 3)):
            mid_count = 0
            bar.update(min(so_far, filesize))
      if (abs(filesize - so_far) <= 1000):
         complete = True
      else:
         try:
            response.close()
         finally:
            outfile.close()
         print "STATUS: Connection dropped, resuming."
         so_far = max(0,so_far-10000)

def main():
   if (len(sys.argv) != 2):
      print "Error: Single URL is required"
      sys.exit(1)
   URL = sys.argv[1]
   # New detection method
   if ("http://www.56.com" in URL):
      print "STATUS: Embedded video URL detected, determining flv URL"
      print "STATUS: Downloading HTML content of:", URL
      f = urllib2.urlopen(URL)
      content = f.read()
      f.close()
      flv_URL = content.split("normal_flv=")[1].split("'")[0]
      print "STATUS: Found intermediate FLV URL:", flv_URL
      opener = urllib2.build_opener(SmartRedirectHandler())
      request = urllib2.Request(flv_URL)
      f = opener.open(request)
      URL = f.url
      print "STATUS: New post redirect URL:", URL
      if (not ("start=" in URL)):
         URL += "&start=0"
      try:
         f.close()
      finally:
         _ = 0
   try:
      variables = dict([(x.split('=')[0],int(x.split('=')[1]) if 
         x.split('=')[1].isdigit() else x.split('=')[1]) for x in URL.split("?")[1].split("&")])
   except:
      print "Error: Malformed variables in:"
      print URL
      print "Should be of form: name=value&name=value...   after single '?'"
      sys.exit(1)
   required_keys = ['start']
   for k in required_keys:
      if (not k in variables.keys()):
         print "Error: %s= missing. URL must be of the format:" % (k)
         print "http://119.188.75.152/fcs45.56.com/flvdownload/5/15/zhajm_12595237589hd.flv?m=s&start=0&end=51167521&s=1"
         print "Get it from: http://www.56.com/w66/album-aid-8080543.html"
         print "Then start playing a video, somewhere in the middle, and traffic capture."
         sys.exit(1)
   base_URL = URL.split('?')[0]
   # ignore the acquired start value, just set it to 0
   variables['start'] = 0
   estimated_length = 0
   print "STATUS: Determining video length"
   new_URL = base_URL + "?start=0&s=1"
   print "STATUS: Checking:", new_URL
   temp_request = urllib2.urlopen(new_URL)
   ignore_byte = temp_request.read(1)
   size_check = int(temp_request.info().getheader('Content-Length'))
   while (size_check == 51200000):
      print "STATUS: Indetermine size, adding 51200000 bytes"
      estimated_length += size_check
      new_URL = (base_URL + "?start=%s&s=1") % (estimated_length)
      print "STATUS: Checking:", new_URL
      try:
         temp_request.close()
      finally:
         temp_request = urllib2.urlopen(new_URL)
      ignore_byte = temp_request.read(1)
      size_check = int(temp_request.info().getheader('Content-Length'))
   # Finally got a real size
   estimated_length += size_check
   print "STATUS: Found real final chunk size:", size_check
   print "STATUS: Total estimated size:", estimated_length
   sustained_transfer(base_URL, estimated_length)
   print "STATUS: Done."

if __name__ == "__main__":
    main()




