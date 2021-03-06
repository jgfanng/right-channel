/** *** load more **** */
$(function() {
	var scroll = 10;
	var isLoading = false;
	var more = true;
	var nextPage = 1;

	function loadMore() {
		if (!isLoading && more) {
			isLoading = true;
			$('#ajaxLoader').show();
			qs = {
				genre : $('#genre').attr('datagenre'),
				country : $('#country').attr('data'),
				year : $('#year').attr('data'),
				sort : $('#sort').attr('data'),
				resource : $('#resource').attr('data'),
				page : nextPage
			};
			$.getJSON('/api/movie', qs, function(data) {
				if (data.movies.length > 0) {
					manipulatePosterTextView(data.movies);
				}
				more = data.more;
				if (more) {
					nextPage = nextPage + 1;
				} else if (data.movies.length === 0 && nextPage === 1) {
					$('#content').empty();
					$('#content').css('text-align', 'center');
					$('#content').append('没有找到符合条件的影片');
				}
			}).complete(function() {
				isLoading = false; // reset the status anyway
				$('#ajaxLoader').hide();
			});
		}
	}

	function manipulatePosterTextView(movies) {
		var html = '';
		for ( var i = 0; i < movies.length; i++) {
			var movie = movies[i];

			{
				var playable = 'resources' in movie && 'online' in movie.resources;
				var poster_img = '<a href="/movie/{0}" class="{1}" target="_blank"><img src="{2}" class="poster-img"><div class="poster-play-mask" style="display: none;"></div></a>'
					.format(
						movie._id,
						playable ? 'playable' : 'notplayable',
						[
							'http://img2.static.dianying.fm/poster/m/5071c79f90d7a90a4169efcd',
							'http://img2.static.dianying.fm/poster/m/5071ccf190d7a90a416a6557',
							'http://img2.static.dianying.fm/poster/m/5071d06190d7a90a416ab147',
							'http://img2.static.dianying.fm/poster/m/50bd066bbf1317525dc37baf',
							'http://img2.static.dianying.fm/poster/m/5127e57b342f10043531121f',
							'http://img2.static.dianying.fm/poster/m/5127e56f342f100435311207',
							'http://img2.static.dianying.fm/poster/m/5071c9c890d7a90a416a21ab',
							'http://img2.static.dianying.fm/poster/m/50bd0a43bf1317525dc37ed9',
							'http://img2.static.dianying.fm/poster/m/5108b686342f1042845f2575',
							'http://img1.static.dianying.fm/poster/m/5071c3d490d7a90a416999f0',
							'http://img1.static.dianying.fm/poster/m/5071c71290d7a90a4169e242',
							'http://img2.static.dianying.fm/poster/m/50df37e9342f1026232ace9d',
							'http://img2.static.dianying.fm/poster/m/5127ccf7342f10043530e341',
							'http://img2.static.dianying.fm/poster/m/5071c07d90d7a90a3c074da9',
							'http://img2.static.dianying.fm/poster/m/5071c65f90d7a90a4169d3a9',
							'http://img1.static.dianying.fm/poster/m/5071c92390d7a90a416a130a',
							'http://img2.static.dianying.fm/poster/m/5071c47490d7a90a4169a883',
							'http://img1.static.dianying.fm/poster/m/5071c4c890d7a90a4169b010',
							'http://img2.static.dianying.fm/poster/m/50bd0eaabf1317525dc382cb',
							'http://img2.static.dianying.fm/poster/m/5071c65b90d7a90a4169d331',
							'http://img2.static.dianying.fm/poster/m/5071ce7390d7a90a416a86d3',
							'http://img2.static.dianying.fm/poster/m/5071d04b90d7a90a416aaff7',
							'http://img1.static.dianying.fm/poster/m/5071c91390d7a90a416a1194',
							'http://img2.static.dianying.fm/poster/m/5071cc1e90d7a90a416a536d',
							'http://img1.static.dianying.fm/poster/m/50bd08e1bf1317525dc37da8',
							'http://img2.static.dianying.fm/poster/m/5071c42990d7a90a4169a1ef',
							'http://img2.static.dianying.fm/poster/m/5071c79790d7a90a4169eef5',
							'http://img2.static.dianying.fm/poster/m/5071c25590d7a90a4169796f',
							'http://img2.static.dianying.fm/poster/m/5127c41a342f10043530d2bf',
							'http://img2.static.dianying.fm/poster/m/5071c40d90d7a90a41699f6f',
							'http://img2.static.dianying.fm/poster/m/5071ccd390d7a90a416a62c9',
							'http://img2.static.dianying.fm/poster/m/5071ce1990d7a90a416a7e9d',
							'http://img1.static.dianying.fm/poster/m/5071c40490d7a90a41699e9a',
							'http://img2.static.dianying.fm/poster/m/5127b514342f107c01c5def5',
							'http://img2.static.dianying.fm/poster/m/5127c042342f10043530cd27',
							'http://img2.static.dianying.fm/poster/m/5071d01190d7a90a416aaa9d',
							'http://img1.static.dianying.fm/poster/m/5071c07290d7a90a3c074c56',
							'http://img1.static.dianying.fm/poster/m/5071c3f690d7a90a41699d42',
							'http://img1.static.dianying.fm/poster/m/5071c4ee90d7a90a4169b388',
							'http://img2.static.dianying.fm/poster/m/5127ee8d342f10043531236b',
							'http://img2.static.dianying.fm/poster/m/5071c55c90d7a90a4169bd0d',
							'http://img1.static.dianying.fm/poster/m/50bd0ed0bf1317525dc382f4',
							'http://img2.static.dianying.fm/poster/m/5071cb3190d7a90a416a3f53',
							'http://img1.static.dianying.fm/poster/m/5071c4ff90d7a90a4169b52c',
							'http://img2.static.dianying.fm/poster/m/5071c67790d7a90a4169d5dd' ][Math
							.floor(Math.random() * 45)]);
				
				var top_div = '';
				if (playable)
					top_div = '<div class="poster-badge poster-badge-top"><a href="/movie/{0}" title="立即观看" target="_blank"><i class="icon-play-circle icon-white"></i></a></div>'.format(movie._id);
				
				var bottom_div = '<div class="poster-badge poster-badge-bottom duration">00:00:00</div>';
				
				var poster_div = '<div class="pull-left poster-container">{0}{1}{2}</div>'.format(poster_img, top_div, bottom_div);
			}

			{
				if ('year' in movie)
					var title_p = '<p><strong><a href="/movie/{0}" target="_blank">{1}</a></strong> <span class="muted">({2})</span></p>'
							.format(movie._id, movie.title, movie.year);
				else
					var title_p = '<p><strong><a href="/movie/{0}" target="_blank">{1}</a></strong></p>'
							.format(movie._id, movie.title);

				var rating_p = ''
				if ('douban' in movie && 'rating' in movie.douban)
					rating_p = '<p><strong>评分:</strong> <a href="{0}" title="豆瓣评分{1}" class="douban-rating" target="_blank"><i class="logo-platform-douban"></i> {1}</a></p>'
							.format(movie.douban.url, movie.douban.rating);

				var genre_p = '';
				if ('genres' in movie && movie.genres.length > 0)
					genre_p = '<p><strong>类型:</strong> {0}</p>'
							.format(movie.genres.join(' / '));

				var cast_p = '';
				if ('casts' in movie && movie.casts.length > 0)
					cast_p = '<p><strong>主演:</strong> {0}</p>'
							.format(movie.casts.join(' / '));

				var desc_div = '<div class="pull-left text-desc">{0}{1}{2}{3}</div>'
						.format(title_p, rating_p, genre_p, cast_p);
			}

			{
				var $to_watch_btn = $('<button data-id="{0}" data-action="towatch" class="btn btn-mini unmarked" title="加入想看列表"><i class="icon-eye-open"></i></button>'
						.format(movie._id));

				var $watched_btn = $('<button data-id="{0}" data-action="watched" class="btn btn-mini unmarked" title="加入看过列表"><i class="icon-check"></i></button>'
						.format(movie._id));

				var $not_interested_btn = $('<button data-id="{0}" data-action="notinterested" class="btn btn-mini unmarked" title="标记为没兴趣"><i class="icon-eye-close"></i></button>'
						.format(movie._id));

				if (movie.to_watch) {
					$to_watch_btn.removeClass('unmarked');
					$to_watch_btn.addClass('marked');
					$to_watch_btn.addClass('btn-info');
					$to_watch_btn.children('i').addClass('icon-white');
					$to_watch_btn.attr('title', '已加入想看列表');
				}
				if (movie.watched) {
					$watched_btn.removeClass('unmarked');
					$watched_btn.addClass('marked');
					$watched_btn.addClass('btn-success');
					$watched_btn.children('i').addClass('icon-white');
					$watched_btn.attr('title', '已加入看过列表');
				}
				if (movie.not_interested) {
					$not_interested_btn.removeClass('unmarked');
					$not_interested_btn.addClass('marked');
					$not_interested_btn.addClass('btn-inverse');
					$not_interested_btn.children('i').addClass('icon-white');
					$not_interested_btn.attr('title', '已标记为没兴趣');
				}

				var toolbar_div = '<div class="btn-group user-interest">{0}{1}{2}</div>'
						.format($to_watch_btn.wrap('<div>').parent().html(), $watched_btn.wrap('<div>').parent().html(), $not_interested_btn.wrap('<div>').parent().html());
			}

			html += '<li><div class="gallery-element">{0}{1}{2}</div></li>'
					.format(poster_div, desc_div, toolbar_div);
		}
		$('#content ul').append(html);
	}

	$(window).scroll(

			function() {
				if ($(window).scrollTop() >= $(document).height()
						- $(window).height() - scroll) {
					loadMore();
				}
			});

	loadMore();
});