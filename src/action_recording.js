// Author: Marco Urbano.
// Date: 27 February 2021.
// Description: the js code that HTTPLogger class will inject to every response from the webserver to the pentester.
//             The objective to record user session even if he/her navigates to different webpages has been
//             achieved exploiting the localStorage of modern web browsers.
// Notes:
//      Credits to MiniWOB++, which ispired me the way to add event listeners. This work differs from MiniWOB++
//      because the latter doesn't allow the user to record a sequence of actions even on different pages, this
//      project aims to allow it because a penetration testing session could require to visit not only one page.


// ################################################
// Record demonstrations

/*
    states: array of objects with the following keys:

  - time: time elapsed
  - dom: DOM structure
  - action: action performed at that moment
*/

var recorder = {};
recorder.listeners = [
                        'click',
                        'dblclick',
                        'mousedown',
                        'mouseup',
                        'keypress',
                        'keydown',
                        'keyup',
                        'load',
                     ];
                     
recorder.addEventListeners = function () {
  recorder.listeners.forEach(function (name) {
    // listen to events when they start and finish.
    document.addEventListener(name, recorder['on' + name], true);
    //document.addEventListener(name, recorder['on' + name], false);
  });
}

// Check if the browser supports localStorage.
function supports_html5_storage() {
  try {
    return 'localStorage' in window && window['localStorage'] !== null;
  } catch (e) {
    return false;
  }
}

// Start recording session or resume it if the page visited is not the first to be recorded.
// Recording will be managed with the help of localStorage feature.
recorder.manageSession = function () {
  if(supports_html5_storage){
    // employed to check if http_request contains "record=true".
    var url_query_string = window.location.search;
    var url_par = new URLSearchParams(url_query_string);
    var record_flag = url_par.get('record');

    // employed to check if session recording was already in execution
    var wapt_session_recording = localStorage['wapt_session_recording']

    // Case 1: the user has finished the demonstration session. This means that the browser needs to send all the
    // events saved so far in localStorage to the mitmproxy server. Data will be sent as JSON.
    if(record_flag == "false"){
        if(localStorage['wapt_session_nrecords'] != null){

            var data = {};
            data['task_name'] = localStorage['wapt_session_taskname'];
            data['window_width'] = localStorage['wapt_session_width'];
            data['window_height'] = localStorage['wapt_session_height'];
            for (var i = 1, n_records = parseInt(localStorage['wapt_session_nrecords']); i < n_records + 1; ++i) {
                record_name = 'wapt_record_' + i;
                record_string = localStorage[record_name];
                data[i] = JSON.parse(record_string);
            }



            // constructing the http request
            var http_req = new XMLHttpRequest();
            // opening the request in asynchronous mode. (the ending true) -- try with syncronous if it works
            http_req.open("POST", window.location.href, true);
            http_req.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

            // sending the collected data as JSON.
            http_req.send(JSON.stringify(data));

            // clearing user's browser localStorage after that the request has been completed.
            localStorage.clear();

            // TODO: here we can check how the request performed.
            // here we can check the response to our POST http request. The most interesting thing to do here is to
            // modify some field in the final HTML page so the user can know that everything went fine and
            // the location of saved files. 09/03/21



        }
        // here we could send a different JSON string in case the user didn't perform any action.
        // code here.
    }
    else if(record_flag == 'true' ||  wapt_session_recording == 'true'){
        // Case 2: the user asked to record his session for the first time, we need to setup the data-structures
        //         that will be employed during session time.
        if(wapt_session_recording == null){
            var url = window.location.pathname;
            // trimming off page extension to have a clean task name.
            localStorage['wapt_session_taskname'] = url.substr(url.lastIndexOf('/') + 1).replace(/\..*/, '');
            localStorage['wapt_session_nrecords'] = 0;
            localStorage['wapt_session_start_time'] = new Date().getTime();
            localStorage['wapt_session_recording'] = true;
            // obtaining window dimension.
            localStorage['wapt_session_width'] = window.innerWidth;
            localStorage['wapt_session_height'] = window.innerHeight;
        }
        // Case 3: session recording was already active and user navigated to a new page / refreshed the same page
        //         with different parameter values. (GET or POST)
        //         Even if the list of events does not contain the page refresh listener, every time that we notice
        //         a change of page we insert a new record into the record action list. (localStorage[wapt_record_X]).

        // recording that user navigated to a new page / refreshed the preceding one with new parameters.
        recorder.navigateTo();



    }


  }
}

// Add a state to the recording data
recorder.addState = function (event, action) {
  if (localStorage['wapt_session_recording'] != null){
    // save action.timing only if this function has been invoked by some eventListener.
    if (event && action) action.timing = event.eventPhase;

    console.log('Adding new record for action: ', action);

    var record = {
    // localStorage contains strings, .getTime() is an Integer representing the number of seconds from EPOCH.
    'time': new Date().getTime() - parseInt(localStorage['wapt_session_start_time']),
    'action': action,
    };
    // record DOM only if this function has been invoked by some eventListener, if this is a simple page refresh
    // or a navigateTo event, do not save the DOM.
    if (event) event.target.dataset.recording_target = true;
    // Remove the tag containing this script to record in order to make the recording code invisible to the end client.

    // create a new dov container
     var temp_div = document.createElement('div');
    // assigning current page innerHTML to div's innerHTML.
     temp_div.innerHTML = document.documentElement.innerHTML;
    // getting node that corresponds to client side recording script.
     var script_element = temp_div.querySelector("[id='wapt_dataset_collector_record']");
    // remove recording script node.
     script_element.parentNode.removeChild(script_element);
    // get div's innerHTML into a new variable
     var html_wo_script = temp_div.innerHTML;

    // Doing this way we only erase the content of node but the empty node is still there in HTML.
    //document.getElementById("wapt_dataset_collector_record").innerHTML = "";

    //record.dom = document.documentElement.innerHTML;
    record.dom = html_wo_script;

    if (event) delete event.target.dataset.recording_target;

    // Add new record to localStorage.
    var n_records = parseInt(localStorage['wapt_session_nrecords']);
    localStorage['wapt_session_nrecords'] = n_records + 1;
    localStorage['wapt_record_' + (n_records + 1)] = JSON.stringify(record);
  }
}

// Actions
recorder.ondblclick = function (event) {
  recorder.addState(event, {
    'type': 'dblclick',
    'x': event.pageX,
    'y': event.pageY,
  });
}
recorder.onclick = function (event) {
  recorder.addState(event, {
    'type': 'click',
    'x': event.pageX,
    'y': event.pageY,
  });
}
recorder.onmousedown = function (event) {
  recorder.addState(event, {
    'type': 'mousedown',
    'x': event.pageX,
    'y': event.pageY,
  });
}
recorder.onmouseup = function (event) {
  recorder.addState(event, {
    'type': 'mouseup',
    'x': event.pageX,
    'y': event.pageY,
  });
}

recorder.onkeypress = function (event) {
  recorder.addState(event, {
    'type': 'keypress',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
    'key': event.key
  });
}
recorder.onkeydown = function (event) {
  recorder.addState(event, {
    'type': 'keydown',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
    'key': event.key
  });
}
recorder.onkeyup = function (event) {
  recorder.addState(event, {
    'type': 'keyup',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
    'key': event.key
  });
}

// useful to mantain a track of urls visited by the pentester.
recorder.navigateTo= function (){
  recorder.addState(null, {
    'type': 'navigateTo',
    'url': window.location.href,
  });
  console.log("navigating to: " + window.location.href);
}

// adding eventListeners to this window.
recorder.addEventListeners();
// managing the session: starts a new recording session when asked from the user, resumes one that is already in
// execution or ends the session and sends actions performed by user to the proxy server when he asks to.
recorder.manageSession();

