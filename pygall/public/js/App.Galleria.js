App = window.App || {};

App.Galleria = {
    init: function() {
		$('ul.gallery_demo').galleria({
			history   : true, // activates the history object for bookmarking, back-button etc.
			clickNext : true, // helper for making the image clickable
			insert    : '#side-b', // the containing selector for our main image
			onImage   : function(image,caption,thumb) { // let's add some image effects for demonstration purposes
				
				// fade in the image & caption
				image.css('display','none').fadeIn(500);
                if(caption.css('display') != 'none') {
                    caption.css('display','none').fadeIn(500);
                }

                if (App.constants.edit) {
                    // TODO put css in a separate stylesheet
                    var edit_caption = $(document.createElement('a')).css({
                        background: '#000',
                        float: 'left',
                        position: 'absolute',
                        display: 'block',
                        right: 0,
                        bottom: 0,
                        padding: '12px',
                        cursor: 'pointer',
                        'z-index': 50,
                        'filter': 'alpha(opacity=60)',
                        '-moz-opacity': 0.6,
                        '-khtml-opacity': 0.6,
                        opacity: 0.6
                    });
                    edit_caption.text('Edit');
                    edit_caption.click(function () {
                        var comment = prompt("Saisir un commentaire : ", caption.text() || "");
                        if(comment == null) {
                            return;
                        }
                        $.post(
                            App.constants.urls.photos_editcomment,
                            {uri:thumb.attr('alt'), comment: comment},
                            function(data, textStatus) {
                                //console.log(data);
                            },
                            'json'
                        );
                        caption.text(comment);
                        thumb.attr('title', comment);
                        if(!comment) {
                            caption.css('display', 'none');
                        } else {
                            caption.css('display', 'block');
                        }
                    });
                    image.after(edit_caption);
                }

				// fetch the thumbnail container
				var _li = thumb.parents('li');
				
                if (_li.attr('title')) {
                    // TODO put css in a separate stylesheet
                    var date_span = $(document.createElement('span')).css({
                        background: '#000',
                        float: 'left',
                        position: 'absolute',
                        display: 'block',
                        left: 0,
                        top: 0,
                        padding: '2px 5px 2px 5px',
                        'z-index': 30,
                        'filter': 'alpha(opacity=60)',
                        '-moz-opacity': 0.6,
                        '-khtml-opacity': 0.6,
                        opacity: 0.6
                    });
                    date_span.text(_li.attr('title'));
                    image.after(date_span);
                }
				
				// fade out inactive thumbnail
				_li.siblings().children('img.selected').fadeTo(500,0.3);
				
				// fade in active thumbnail
				thumb.fadeTo('fast',1).addClass('selected');
				
				// add a title for the clickable image
				image.attr('title','Next image >>');
			},
			onThumb : function(thumb) { // thumbnail effects goes here
				
				// fetch the thumbnail container
				var _li = thumb.parents('li');
				
				// if thumbnail is active, fade all the way.
				var _fadeTo = _li.is('.active') ? '1' : '0.3';
				
				// fade in the thumbnail when finnished loading
				thumb.css({display:'none',opacity:_fadeTo}).fadeIn(1500);
				
				// hover effects
				thumb.hover(
					function() { thumb.fadeTo('fast',1); },
					function() { _li.not('.active').children('img').fadeTo('fast',0.3); } // don't fade out if the parent is active
				)
			}
		});
    }
};
