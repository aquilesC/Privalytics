var privalytics = function (privalytics_id) {
    if (!window) return;
    var url = window.location;
    var document = window.document;
    var navigator = window.navigator;

    var data = {url: url};
    if (document.referrer) data.referrer = document.referrer;
    if (window.innerWidth) data.width = window.innerWidth;
    if (window.innerHeight) data.height = window.innerHeight;
    // If do not track is enabled, we wont store any personal information on our servers
    if ('doNotTrack' in navigator && navigator.doNotTrack === "1") {
        data.dnt = true;
    }
    data.account_id = privalytics_id;

    var request = new XMLHttpRequest();
    request.open('POST', 'https://www.privalytics.io/api/tracker', true);
    request.setRequestHeader('Content-Type', 'text/plain; charset=UTF-8');
    request.send(JSON.stringify(data));
};
privalytics(privalytics_id);