$(function() {
	var scroll = 10;
	var isLoading = false;
	var hasMore = true;
	var nextPage = 1;

	function loadMore() {
		if (!isLoading && hasMore) {
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
				hasMore = data.has_more;
				if (hasMore) {
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
		var currLength = $('#content ul.gallery').children().length;
		var elementsInRow = 3;
		var html = '';
		for ( var i = 0; i < movies.length; i++) {
			var movie = movies[i];

			var poster_div = '<div class="pull-left poster-medium"><a href="/movie/{0}" target="_blank"><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQQAAAC0CAYAAABytVLLAAAIhElEQVR4Xu3avYsUWxMH4N7AL9DARM1EDNVQBP99IxMxUoxFMJBFENHAj/ftgbO07cxsrXW99K16TMT1TM2pp7p/0907J6enpz8nfwgQIPB/gROB4DggQGAICATHAgECZwICwcFAgIBAcAwQIPC7gCsERwUBAq4QHAMECLhCcAwQIHBEwC2Dw4MAAbcMjgECBNwyOAYIEHDL4BggQCAi4BlCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgNBm0NglEBARCRMkaAk0EBEKTQWuTQERAIESUrCHQREAgbHDQr1+/nt69e3e2sxs3bkxPnjz5Zaenp6fTy5cvpx8/fux+vm/N27dvpzdv3py97t69e9P9+/f/uOMXL15M8/vevn17evTo0S91xv+NH+5b80/v548b8cKDAgJhYwfH+sQa21ue8Osw2HcSrk++seZPQ2FZb32yrwPs39jPxsZWZjsCYUOj/Pbt2/Ts2bPp+/fv0zhxlyfiw4cPp1u3bk3Pnz+fPn/+/Nuak5OT6enTp9OVK1fO1oyTd5y0V69e3V1tXLp0Kdz5sU//5Z7X7/W39hPeuIUXFhAIFyb7ey8YJ/84ka5duzatQ+Lu3bu70JhvFeaTf16z/rO8gphD5M6dO7tL/fkW4+fPn7vXffny5eyWY4TP+nXL8JnfYw6Tr1+//nLLsNxf5L0OrdnXx9+TVvmQgEDY+LGxPkkvX768O5Hnv+cT9OPHj7sOlpfx65N/HSzjpByf/HOdx48fT/O/5yuPUWsOnflq5Pr169ODBw9+u+qY33esWb5ufTXy6dOnX8Lo0H42PooW2xMIGx7z8mQbzxAOPRuY21ivOXalMT9cXH66z1cR79+/n5avWdLsO/HH/y/rjJ8t60SufDIPOzc8wv/c1gTCRke2PAH3nVzzttfPGca6Dx8+7H67cF4gzDWiT/6PBcJ5DzAFwkYPsj3bEggbnNWhMJi3GrkdGLcV43nBsUv05af7oauDQ7cG88+PPQgd9cbzish+NjiOVlsSCBsb97EwuGggzLXOe4i3/pXhvu8PHAuEyKf/zZs3zx5gnrefjY2j3XYEwsZGPh70XeRefn1SRn/tuLzamB8avnr1aveQcJy0kWcIy4eekV+V/hO/Bt3YyEptRyBsaJyHvnA0trjvhFtuf/npft59feS3A8vvKhx6hrD8+Zpy+WWq8/azoTG03opA2ND4D33jbx0Iy1uH8dXli35VeLzXoQeP63rHHirO+1l/eenf+Cr1hkZXZisCocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgLyAQ8oYqECgjIBDKjFIjBPICAiFvqAKBMgICocwoNUIgL/A/1uMQYymAtG0AAAAASUVORK5CYII="></a></div>'
					.format(movie._id);

			{
				if ('year' in movie)
					var title_p = '<p><a href="/movie/{0}" target="_blank" class="title">{1}</a> <span class="year">({2})</span></p>'
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
				var watch_li = '';
				if ('online' in movie && movie.online.length > 0)
					watch_li = '<li><a href="/movie/{0}" target="_blank" title="立即观看"><i class="icon-play"></i></a></li>'
							.format(movie._id);

				var download_li = '';
				if ('download' in movie && movie.download.length > 0)
					download_li = '<li><a href="/movie/{0}" target="_blank" title="立即下载"><i class="icon-download-alt"></i></a></li>'
							.format(movie._id);

				var to_watch_li = '<button id="toWatch" class="btn btn-mini" title="想看" data-id="{0}"><i class="icon-heart"></i> 想看</button>'
						.format(movie._id);
				var watched_li = '<button id="watched" class="btn btn-mini" title="看过" data-id="{0}"><i class="icon-check"></i> 看过</button>'
						.format(movie._id);

				var toolbar_div = '<div class="toolbar btn-group">{0}{1}</div>'
						.format(to_watch_li, watched_li);
			}

			if ((i + currLength) % elementsInRow == elementsInRow - 2) {
				if ((i + currLength) < elementsInRow)
					html += '<li class="first-row penultimate-child"><div class="gallery-element">{0}{1}{2}</div></li>'
							.format(poster_div, desc_div, toolbar_div);
				else
					html += '<li class="penultimate-child"><div class="gallery-element">{0}{1}{2}</div></li>'
							.format(poster_div, desc_div, toolbar_div);
			} else if ((i + currLength) % elementsInRow == elementsInRow - 1) {
				if ((i + currLength) < elementsInRow)
					html += '<li class="first-row last-child"><div class="gallery-element">{0}{1}{2}</div></li>'
							.format(poster_div, desc_div, toolbar_div);
				else
					html += '<li class="last-child"><div class="gallery-element">{0}{1}{2}</div></li>'
							.format(poster_div, desc_div, toolbar_div);
			} else {
				if ((i + currLength) < elementsInRow)
					html += '<li class="first-row"><div class="gallery-element">{0}{1}{2}</div></li>'
							.format(poster_div, desc_div, toolbar_div);
				else
					html += '<li><div class="gallery-element">{0}{1}{2}</div></li>'
							.format(poster_div, desc_div, toolbar_div);
			}
		}
		$('#content ul.gallery').append(html);
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