$(function(){
    var url = 'http://' + document.domain + ':' + location.port + '/users';

    $("#grid").dxDataGrid({
        dataSource: DevExpress.data.AspNet.createStore({
            key: "id",
            loadUrl: url ,
            insertUrl: url ,
            updateUrl: url ,
            deleteUrl: url ,
            onBeforeSend: function(method, ajaxOptions) {
                ajaxOptions.xhrFields = { withCredentials: true };
            }
        }),
        editing: {
            mode: "row",
            allowUpdating: true,
            allowDeleting: true,
            allowAdding: true,
            useIcons: true
        },
        remoteOperations: {
            sorting: true,
            paging: true
        },
        paging: {
            pageSize: 12
        },
        pager: {
            showPageSizeSelector: true,
            allowedPageSizes: [8, 12, 20]
        },
        onRowInserting: function(e) {
            var username = e.username;

            if(username == null) {
                e.errorText = "Username is required";
                e.isValid = false;
            }
        },
        onRowUpdating: function(e) {
            var username = e.username;

            if(username == null) {
                e.errorText = "Username is required";
                e.isValid = false;
            }
        },
        /*onRowValidating: function(e) {
            var username = e.newData.username;

            if(username == null) {
                e.errorText = "Username is required";
                e.isValid = false;
            }
        },*/
        columns: [{
                    dataField: "id",
                    dataType: "number",
                    allowEditing: false
                  }, {
                    dataField: "username",
                    validationRules: [{ type: "required" }]
                  }, {
                    dataField: "email",
                    validationRules: [{ type: "required" }, { type: "email" }]
                    //allowEditing: false
                  }, {
                    dataField: "name",
                    validationRules: [{ type: "required" }]
                  }, {
                    dataField: "fullname"
                  }, {
                    dataField: "password",
                    allowEditing: false,
                    
                    validationRules: [{ type: "required" }]
                  }, ],
                 }).dxDataGrid("instance");
});
