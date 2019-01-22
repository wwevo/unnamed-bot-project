$(document).ready(function() {
    // https://stackoverflow.com/a/46308265
    $.fn.upsert = function(selector, htmlString) {
        // upsert - find or create new element
        // find based on css selector     https://api.jquery.com/category/selectors/
        // create based on jQuery()       http://api.jquery.com/jquery/#jQuery2
        let $el = $(this).find(selector);
        if ($el.length === 0) {
            // didn't exist, create and add to caller
            $el = $(htmlString);
            $(this).append($el);
        }

        return $el;
    };

    //connect to the socket server.
    window.socket = io.connect(
        'http://' + document.domain + ':' + location.port + '/chrani-bot-ng'
    );

    window.socket.on('connected', function() {
        console.log("connected...");
        window.socket.emit('ding');
        console.log("sent 'ding' to server");
    });

    window.socket.on('dong', function() {
        console.log("got 'dong' from server");
        window.setTimeout(
            function () {
                window.socket.emit('ding');
                console.log("sent 'ding' to server");
            },
            15000);
    });

    window.socket.on('data', function(data) {
        if (data["data_type"] == "widget_content") {
            let $el = $("body > main > div").upsert('#' + data["target_element"], '<div class="widget" id="' + data["target_element"] + '"></div>');
            if (data["method"] === "update") {
                $el.html(data["event_data"]);
            } else if (data["method"] === "append") {
                $el.append(data["event_data"]);
            } else if  (data["method"] === "prepend") {
                $el.prepend(data["event_data"]);
            }
        } else if (data["data_type"] == "status_message") {
            console.log("received status '" + data['status'] + "' for event '" + data['event_data'][0] + "' from server");
        }
    });

});

