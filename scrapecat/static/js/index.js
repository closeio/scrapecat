$('#ScrapeRequestForm').ajaxForm({
    beforeSubmit: function() {
        $('form#ScrapeRequestForm button#submit').addClass('disabled').removeClass('btn-primary');
    },
    dataType: 'json',
    target: '#ScrapeRequestFormResults',
    success: function(results) {
        function renderContacts(contacts) {
            for (var i = 0; i < contacts.length; i++){
                var contact = ich.contact(contacts[i]);
                $('table#contacts').append(contact);
            }
        };
        function renderElement(type, list) {
            type_singular = type.substring(0, type.length - 1);
            for (var i = 0; i < list.length; i++) {
                var d = {};
                d[type_singular] = list[i];
                var el = ich[type_singular](d);
                $('#ScrapeRequestFormResults .' + type + ' ul').append(el);
            }
        }
        $('form#ScrapeRequestForm button#submit').addClass('btn-primary').removeClass('disabled');
        for (var type in results) {
            if (results.hasOwnProperty(type)){
                values = results[type]
                if (type == "contacts")
                    renderContacts(values)
                else if (type == "phones" || type == "emails")
                    renderElement(type, values);
            }
        }
        $('#ScrapeRequestFormResults').show(500);
    },
});
