$('#ScrapeRequestForm').ajaxForm({
    beforeSubmit: function() {
        $('form#ScrapeRequestForm button#submit').addClass('disabled').removeClass('btn-primary');
    },
    dataType: 'json',
    target: '#ScrapeRequestFormResults',
    success: function(results) {
        function renderContacts(contacts) {
            for (var i = 0; i < contacts.length; i++){
                $('table#contacts').append("<tr><td>" + contacts[i].phones +"</td><td>" + contacts[i].emails + "</td></tr>");
            }
        };
        $('form#ScrapeRequestForm button#submit').addClass('btn-primary').removeClass('disabled');
        for (var type in results) {
            if (results.hasOwnProperty(type)){
                values = results[type]
                if (type == "contacts")
                    renderContacts(values)
                else
                    for (var i = 0; i < values.length; i ++)
                        $('#ScrapeRequestFormResults .' + type + ' ul').append("<li>" + values[i] + "</li>");
            }
        }
        $('#ScrapeRequestFormResults').show(500);
    },
});
