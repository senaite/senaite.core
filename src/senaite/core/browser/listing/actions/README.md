# Listing actions

A listing action is basically a browser view that get asynchornously executed
from a listing view.

Therefore, it must return a JSON message with the following contents:

``` json
{
  "message": "Return message of the action",
  "success": true/false
  "title": "Action title"
}
```

