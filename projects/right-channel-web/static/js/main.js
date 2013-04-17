/** *** utilities **** */
$(function() {
	String.prototype.format = function() {
		var s = this;
		for ( var i = 0; i < arguments.length; i++) {
			var reg = new RegExp('\\{' + i + '\\}', 'gm');
			s = s.replace(reg, arguments[i]);
		}

		return s;
	};
});

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
				genre : $('#genre').attr('data-genre'),
				country : $('#country').attr('data-country'),
				year : $('#year').attr('data-year'),
				sort : $('#sort').attr('data-sort'),
				resource : $('#resource').attr('data-resource'),
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

			var poster_div = '<div class="pull-left"><a href="/movie/{0}" target="_blank"><img src="{1}" class="poster-medium"></a></div>'
					.format(
							movie._id,
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

			{
				if ('year' in movie)
					var title_p = '<p><a href="/movie/{0}" target="_blank" class="title">{1}</a> <span class="muted">({2})</span></p>'
							.format(movie._id, movie.title, movie.year);
				else
					var title_p = '<p><a href="/movie/{0}" target="_blank" class="title">{1}</a></p>'
							.format(movie._id, movie.title);

				var rating_p = ''
				if ('douban' in movie && 'rating' in movie.douban)
					rating_p = '<p><strong>评分:</strong> <span class="rating" title="豆瓣评分{0}">{0}</span></p>'
							.format(movie.douban.rating);

				var genre_p = '';
				if ('genres' in movie && movie.genres.length > 0)
					genre_p = '<p><strong>类型:</strong> {0}</p>'
							.format(movie.genres.join(' / '));

				var cast_p = '';
				if ('casts' in movie && movie.casts.length > 0)
					cast_p = '<p><strong>主演:</strong> {0}</p>'
							.format(movie.casts.join(' / '));

				var desc_div = '<div class="pull-left desc">{0}{1}{2}{3}</div>'
						.format(title_p, rating_p, genre_p, cast_p);
			}

			{
				var $to_watch_btn = $('<button id="toWatch" data-id="{0}" class="btn btn-mini" title="想看本片"><i class="icon-eye-open"></i> 想看</button>'
						.format(movie._id));

				var $watched_btn = $('<button id="watched" data-id="{0}" class="btn btn-mini" title="已看本片"><i class="icon-check"></i> 已看</button>'
						.format(movie._id));

				if (movie.watched) {
					$to_watch_btn.hide();
					$watched_btn.addClass('active');
					$watched_btn.attr('title', '取消已看');
				} else if (movie.to_watch) {
					$to_watch_btn.addClass('active');
					$to_watch_btn.attr('title', '取消想看');
				}

				var toolbar_div = '<div class="btn-group toolbar">{0}{1}</div>'
						.format($to_watch_btn.wrap('<div>').parent().html(), $watched_btn.wrap('<div>').parent().html());
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

/** *** movie category: ignored, to watch, watched **** */
$(function() {
	$('#content').on('click', function(e) {
		var $btn = $(this);
		if (!$btn.hasClass('disabled')) {
			if (!$btn.hasClass('active')) {
				var movie_id = $btn.attr('data-id');
				$btn.addClass('disabled');
				$.ajax({
					type : 'POST',
					url : '/api/movie/towatch',
					data : {
						id : movie_id
					}
				}).done(function() {
					$btn.attr('title', '取消想看');
					$btn.addClass('active');
				}).fail(function(jqXHR) {
					if (jqXHR.status == 401) { // unauthorized
						$.cookie.raw = true;
						$.cookie('next', window.location.href);
						window.location.href = '/login';
					}
				}).always(function() {
					$btn.removeClass('disabled');
				});
			} else {
				var movie_id = $btn.attr('data-id');
				$btn.addClass('disabled');
				$.ajax({
					type : 'delete',
					url : '/api/movie/towatch/' + movie_id
				}).done(function() {
					$btn.attr('title', '想看本片');
					$btn.removeClass('active');
				}).fail(function(jqXHR) {
					if (jqXHR.status == 401) { // unauthorized
						$.cookie.raw = true;
						$.cookie('next', window.location.href);
						window.location.href = '/login';
					}
				}).always(function() {
					$btn.removeClass('disabled');
				});
			}
		}
	}).on('click', '#watched', function(e) {
		var $btn = $(this);
		if (!$btn.hasClass('disabled')) {
			if (!$btn.hasClass('active')) {
				var movie_id = $btn.attr('data-id');
				$btn.addClass('disabled');
				$.ajax({
					type : 'post',
					url : '/api/movie/watched',
					data : {
						id : movie_id
					}
				}).done(function() {
					$btn.attr('title', '取消已看');
					$btn.addClass('active');
					// deal with toWatch button
					var $toWatchBtn = $btn.prev();
					$toWatchBtn.attr('title', '想看本片');
					$toWatchBtn.removeClass('active');
					$toWatchBtn.hide();
					// $btn.closest('li').hide()
				}).fail(function(jqXHR) {
					if (jqXHR.status == 401) { // unauthorized
						$.cookie.raw = true;
						$.cookie('next', window.location.href);
						window.location.href = '/login';
					}
				}).always(function() {
					$btn.removeClass('disabled');
				});
			} else {
				var movie_id = $btn.attr('data-id');
				$btn.addClass('disabled');
				$.ajax({
					type : 'delete',
					url : '/api/movie/watched/' + movie_id
				}).done(function() {
					$btn.attr('title', '已看本片');
					$btn.removeClass('active');
					// deal with toWatch button
					var $toWatchBtn = $btn.prev();
					$toWatchBtn.attr('title', '想看本片');
					$toWatchBtn.removeClass('active');
					$toWatchBtn.show();
				}).fail(function(jqXHR) {
					if (jqXHR.status == 401) { // unauthorized
						$.cookie.raw = true;
						$.cookie('next', window.location.href);
						window.location.href = '/login';
					}
				}).always(function() {
					$btn.removeClass('disabled');
				});
			}
		}
	}).on('click', '#ignored', function(e) {
		var $btn = $(this);
		if (!$btn.hasClass('disabled')) {
			var movie_id = $btn.attr('data-id');
			$btn.addClass('disabled');
			$.ajax({
				type : 'post',
				url : '/api/movie/ignored',
				data : {
					id : movie_id
				}
			}).done(function() {
				$btn.attr('id', 'unwatched');
				$btn.attr('title', '取消忽略');
				$btn.addClass('active');
				$btn.closest('li').hide()
			}).fail(function(jqXHR) {
				if (jqXHR.status == 401) { // unauthorized
					$.cookie.raw = true;
					$.cookie('next', window.location.href);
					window.location.href = '/login';
				}
			}).always(function() {
				$btn.removeClass('disabled');
			});
			;
		}
	}).on('click', '#unignored', function(e) {
		var $btn = $(this);
		if (!$btn.hasClass('disabled')) {
			var movie_id = $btn.attr('data-id');
			$btn.addClass('disabled');
			$.ajax({
				type : 'delete',
				url : '/api/movie/ignored/' + movie_id
			}).done(function() {
				$btn.attr('id', 'ignored');
				$btn.attr('title', '忽略本片');
				$btn.removeClass('active');
			}).fail(function(jqXHR) {
				if (jqXHR.status == 401) { // unauthorized
					$.cookie.raw = true;
					$.cookie('next', window.location.href);
					window.location.href = '/login';
				}
			}).always(function() {
				$btn.removeClass('disabled');
			});
		}
	});
});