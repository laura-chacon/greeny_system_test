import falcon, requests
import json
import random

def get(url, query_string, auth_token, expected_status_code):
    headers = {"Accept": "application/json"}
    if auth_token != None:
        headers.update({"Token": auth_token})
    r = requests.get(
        "http://127.0.0.1:8005" + url,
        params=query_string,
        headers=headers
    )
    assert r.status_code == expected_status_code
    return json.loads(r.content)

def put(url, request_body, auth_token, expected_status_code):
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}
    if auth_token != None:
        headers.update({"Token": auth_token})
    r = requests.put(
        "http://127.0.0.1:8005" + url,
        data=json.dumps(request_body),
        headers=headers
    )
    assert r.status_code == expected_status_code
    return json.loads(r.content)

def post(url, request_body, expected_status_code):
    r = requests.post(
        "http://127.0.0.1:8005" + url,
        data=json.dumps(request_body),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json"}
    )
    assert r.status_code == expected_status_code
    return json.loads(r.content)

def setup(ctxt):
    email = "testing" + str(random.randint(0,1000000)) + "@gmail.com"
    password = "111222"
    return {"email": email, "password": password}

def get_user_with_email_assert_not_found(ctxt):
    query_string = {'email': ctxt["email"]}
    body = get("/users", query_string, None, 200)
    assert "users" in body.keys()
    assert "uid" in body.keys()
    assert body['users'] == []
    return {"uid": body["uid"]}

def signup(ctxt):
    request_body = {'email': ctxt["email"], 'password': ctxt["password"]}
    body = put("/users/" + str(ctxt["uid"]), request_body, None, 200)
    assert "auth_token" in body.keys()
    return {"auth_token": body["auth_token"]}

def get_user_with_email_assert_found(ctxt):
    query_string = {'email': ctxt["email"]}
    body = get("/users", query_string, None, 200)
    assert "users" in body.keys()
    assert body['users'] == [{"uid": ctxt["uid"]}]
    return {}

def login(ctxt):
    request_body = {"password": ctxt["password"]}
    body = post("/users/" + ctxt["uid"] + "/validate_password", request_body, 200)
    assert "token" in body.keys()
    assert body['token'] != ctxt["auth_token"]
    return {"auth_token": body["token"]}

def get_facts(ctxt):
    body = get("/facts", {}, None, 200)
    assert "display" in body.keys()
    return {}

def get_sections(ctxt):
    body = get("/sections", {}, None, 200)
    assert "sections" in body.keys()
    assert len(body['sections']) > 0
    return {}

def get_action_types(ctxt):
    body = get("/sections/water/actions", {}, None, 200)
    assert "action_types" in body.keys()
    assert len(body["action_types"]) > 0
    return {}

def get_next_action_id(ctxt):
    body = get("/users/" + ctxt["uid"] + "/actions/next_id", {}, None, 200)
    assert "next_action_id" in body.keys()
    return {"next_action_id": body["next_action_id"]}

def create_action(ctxt):
    url = "/users/" + ctxt["uid"] + "/actions/" + ctxt["next_action_id"]
    request_body = {"section": "foo", "action_type": "bar", "score": "5"}
    body = put(url, request_body, ctxt["auth_token"], 200)
    return {}

def create_action_unauthorized(ctxt):
    url = "/users/" + ctxt["uid"] + "/actions/" + ctxt["next_action_id"]
    request_body = {}
    body = put(url, request_body, "foobar", 401)
    return {}

def get_history(ctxt):
    body = get("/users/" + ctxt["uid"] + "/history", {}, ctxt["auth_token"], 200)
    assert "user_history" in body.keys()
    assert len(body["user_history"]) == 2
    return {}

def run_steps(steps):
    def run_step(ctxt, step):
        new_ctxt_fields = step(ctxt)
        ctxt.update(new_ctxt_fields)
        return ctxt
    reduce(run_step, steps, {})

steps = [setup,
         get_user_with_email_assert_not_found,
         signup,
         get_user_with_email_assert_found,
         login,
         get_facts,
         get_sections,
         get_action_types,
         get_next_action_id,
         create_action,
         get_next_action_id,
         create_action,
         create_action_unauthorized,
         get_history]
run_steps(steps)
