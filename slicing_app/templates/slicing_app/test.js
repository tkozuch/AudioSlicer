(function(){
  var json_dump = "{{ data }}";
  var task_id = "{{task_id}}";
  var progress_bar = jQuery('.progress-bar');

  var refreshIntervalId = setInterval(function() {
      $.ajax({
            url:'get_progress/',
            type: 'POST',
            data: {
                task_id: task_id,
                csrfmiddlewaretoken: "{{ my_csrf_token }}",
            },
            success: function(result) {
                if (result.state == 'PENDING') {
                    progress_bar.html('Please wait...');
                }
                else if(result.state != 'SUCCESS'){
                        progress_bar.css({'width': result.details.percent + '%'});
                        progress_bar.html(result.details.current + '/' + result.details.total);
                }
                else {
                        progress_bar.css({'width': '100%'});
                        progress_bar.html('Done! Your file has been sliced.');
                        $("#wait").html("Files ready for download: ");
                        var urls = result.urls;
                        var names = result.names;
                        createHtmlForDownloadLinks(urls, names);
                        clearInterval(refreshIntervalId);
                }
            },
      });
  },1000);


  function createHtmlForDownloadLinks(urls, names){
    var links_list = $("#links-list");
    var html = "";
    for (i = 0; i < names.length; i++) {
      url = urls[i];
      name = names[i];
      html += "<br><a href=\"" + url + "\" download>" + name + "</a>";
    }
    links_list.html(html);
  };