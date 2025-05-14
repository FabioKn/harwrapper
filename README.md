# Licence
This project includes components licensed under the Apache License 2.0. See THIRD_PARTY_LICENSES.md for details.
# harwrapper
Wrapper for fixing HAR files (in a special usecase, where "{"log": '(content)' }" is missing) and converting with har2warc


# what is it good for
If a .har file starts with

```{"version":"1.2","creator":{```

har2warc can't convert it, because it misses the log-entry.
In this case the harwrapper adds the missing text to the dict before converting it to a warc.

Harwrapper handles as well a single file as a whole folder.
