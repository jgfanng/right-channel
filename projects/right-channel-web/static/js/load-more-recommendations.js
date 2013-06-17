/** *** load more recommendations **** */
$(function() {
	var scroll = 10;
	var isLoading = false;
	var more = true;
	var nextStart = 0;
	var LIMIT = 30;

    function loadNextPage() {
        loadMoreRecommendations(nextStart, LIMIT);
    }
    
    function loadNextRecommendation() {
        loadMoreRecommendations(nextStart, 1);
    }

	function loadMoreRecommendations(start, limit) {
		if (!isLoading && more) {
			isLoading = true;
			$('#ajaxLoader').show();
            $.ajax({
                type : 'GET',
                url : '/api/movie/recommendation',
                data : {
                    start: start,
                    limit: limit
                },
                dataType: 'json'
            }).done(function(data) {
                manipulateView(data.movies);
                more = data.more;
                if (more) {
                    nextStart = start + limit;
                }
                if (data.movies.length == 0 && nextStart == 0) {
                    $('#content').empty();
                    $('#content').css('text-align', 'center');
                    $('#content').append('没有找到值得推荐的电影');
                }
            }).fail(function(jqXHR) {
                if (jqXHR.status == 401) { // unauthorized
                    $.cookie.raw = true;
                    $.cookie('next', window.location.href);
                    window.location.href = '/login';
                } else {
                    //showOperationAlert(false, '标记失败');
                }
            }).always(function() {
                isLoading = false; // reset the status anyway
                $('#ajaxLoader').hide();
            });
		}
	}

	function manipulateView(movies) {
		var html = '';
		for (var i = 0; i < movies.length; i++) {
			var movie = movies[i];
            var poster_img = '<a href="/movie/{0}" target="_blank"><img src="http://img3.douban.com/lpic/s11356673.jpg" class="poster-medium"></a>'.format(movie._id);
            var top_div = '<div class="poster-badge poster-badge-top caption">{0}</div>'.format(movie.title);
            var bottom_div = '<div class="poster-badge poster-badge-bottom duration">00:00:00</div>';
            html += '<li><div class="poster-gallery-element">{0}{1}{2}</div></li>'.format(poster_img, top_div, bottom_div);
		}
		$('#content ul').append(html);
	}

	$(window).scroll(
			function() {
				if ($(window).scrollTop() >= $(document).height()
						- $(window).height() - scroll) {
					loadNextPage();
				}
			});
			
	loadNextPage();
});