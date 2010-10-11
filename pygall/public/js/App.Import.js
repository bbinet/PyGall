App = window.App || {};

App.Import = {
    init: function() {
        $("table#photos-tree").treeTable({
            initialState: "expanded"
        });

        // make visible that a row is clicked
        $("table#photos-tree tbody tr").mousedown(function() {
            $("tr.selected").removeClass("selected"); // Deselect currently selected rows
            $(this).addClass("selected");
        });

        // make sure row is selected when span is clicked
        $("table#photos-tree tbody tr span").mousedown(function() {
            $($(this).parents("tr")[0]).trigger("mousedown");
        });

        $("#btn_import").click(function() {
            $('#flash').text(''); // reinit flash message
            $('table#photos-tree tbody tr input:checked')
            .each(function() {
                // do not send request for directories
                if ($(this).parents("tr").find("td span").attr('class') == 'file') {
                    var path = $(this).parents("tr").find("td span").text();
                    $.post(
                        App.constants.urls.photos,
                        { path: path },
                        function(response){
                            if (response.status == true) {
                                $('table#photos-tree tbody tr td span.file').filter(
                                    function(){
                                        return $(this).text()==path;
                                    }
                                ).parents("tr").remove();
                            }
                            else {
                                var current_flash = $('#flash').html();
                                if (current_flash) {
                                    current_flash += "<br />";
                                    }
                                $('#flash').html(current_flash + response.msg);
                            }
                        },
                        "json"
                    );
                }
            });
        });

        $("#btn_delete").click(function() {
            $('#flash').text(''); // reinit flash message
            $('table#photos-tree tbody tr input:checked')
            .each(function() {
                // do not send request for directories
                if ($(this).parents("tr").find("td span").attr('class') == 'file') {
                    var path = $(this).parents("tr").find("td span").text();
                    $.post(
                        App.constants.urls.import_delete,
                        { path: path },
                        function(response){
                            if (response.status == true) {
                                $('table#photos-tree tbody tr td span.file').filter(
                                    function(){
                                        return $(this).text()==path;
                                    }
                                ).parents("tr").remove();
                            }
                        },
                        "json"
                    );
                }
            });
        });

        // checking nodes will check corresponding leafs
        $('.folder').parent().siblings().children('input[type="checkbox"]').change(function() {
            $('.child-of-node-'+this.value+' input')
            .attr('checked', $(this).is(':checked'))
            .trigger('change');
        });
    }
};
