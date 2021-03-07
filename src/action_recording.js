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
                        'scroll',
                        'load',
                     ];
                     
recorder.addEventListeners = function () {
  recorder.listeners.forEach(function (name) {
    // listen to events when they start and finish.
    document.addEventListener(name, recorder['on' + name], true);
    document.addEventListener(name, recorder['on' + name], false);
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
    // events saved so far in localStorage to the mitmproxy server. The data will be sent as JSON.
    if(record_flag == 'false'){
        if(localStorage['wapt_session_n_rec'] != null){

            var data = {};
            data['task_name'] = localStorage['wapt_session_taskname'];

            for (var i = 0, n_records = parseInt(localStorage['wapt_session_n_rec']); i < n_records; ++i) {
                record_name = 'wapt_record_' + i;
                data[record_name] = localStorage[record_name];
            }

            // constructing the http request
            var http_req = new XMLHttpRequest();
            // opening the request in asynchronous mode. (the ending true) -- try with syncronous if it works
            http_req.open("POST", window.location.href, true);
            http_req.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

            // sending the collected data as JSON.
            http_req.send(JSON.stringify(data));

            // here we can check how the request performed.
            // code here.


            // clearing user's browser localStorage after that the request has been completed.
            localStorage.clear();
        }
        // here we could send a different JSON string in case the user didn't perform any action.
        // code here.
    }
    else if(record_flag == 'true' ||  wapt_session_recording == 'true'){
        // Case 2: the user asked to record his session for the first time, we need to setup the data-structures
        //         that will be employed during session time.
        if(wapt_session_recording == null){
            var url = window.location.pathname;
            // TODO: perform replace with a updated list of most used webpages extension. (not only .jsp, as seen in wavsep pages)
            localStorage['wapt_session_taskname'] = url.substr(url.lastIndexOf('/') + 1).replace(/\.jsp/, '');
            localStorage['wapt_session_nrecords'] = 0;
            localStorage['wapt_session_start_time'] = new Date().getTime();
            localStorage['wapt_session_recording'] = true;
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
  if (event && action && localStorage['wapt_session_recording'] != null){
    action.timing = event.eventPhase;
    console.log('Adding new record for action: ', action);

    var record = {
    // localStorage contains strings, .getTime() is an Integer representing the number of seconds from EPOCH.
    'time': new Date().getTime() - parseInt(localStorage['wapt_session_start_time']),
    'action': action,
    };
    if (event) event.target.dataset.recording_target = true;
    record.dom = document.documentElement.outerHTML;
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
  });
}
recorder.onkeydown = function (event) {
  recorder.addState(event, {
    'type': 'keydown',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
  });
}
recorder.onkeyup = function (event) {
  recorder.addState(event, {
    'type': 'keyup',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
  });
}

recorder.onscroll = function (event) {
  // Scroll is super redundant; only keep the first one
  if (recorder.data.states.length) {
    var lastState = recorder.data.states[recorder.data.states.length - 1];
    if (lastState.action && lastState.action.type === 'scroll')
      return;
      //recorder.data.states.pop();     // <-- use this for keeping the last one
  }
  recorder.addState(event, {
    'type': 'scroll',
  });
}

recorder.navigateTo= function (event){
  recorder.addState(null, {
    'type': 'navigateTo',
    'url': window.location.href,
  });
  //console.log(window.location.href);
}
window._getRecordedStates = function() { return recorder.data.states; };

// adding eventListeners to this window.
recorder.addEventListeners()
// managing the session: starts a new recording session when asked from the user, resumes one that is already in
// execution or ends the session and sends actions performed by user to the proxy server when he asks to.
recorder.manageSession()

