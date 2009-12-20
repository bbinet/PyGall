/**
 * Galleria (http://monc.se/kitchen)
 *
 * Galleria is a javascript image gallery written in jQuery. 
 * It loads the images one by one from an unordered list and displays thumbnails when each image is loaded. 
 * It will create thumbnails for you if you choose so, scaled or unscaled, 
 * centered and cropped inside a fixed thumbnail box defined by CSS.
 * 
 * The core of Galleria lies in it's smart preloading behaviour, snappiness and the fresh absence 
 * of obtrusive design elements. Use it as a foundation for your custom styled image gallery.
 *
 * MAJOR CHANGES v.FROM 0.9
 * Galleria now features a useful history extension, enabling back button and bookmarking for each image.
 * The main image is no longer stored inside each list item, instead it is placed inside a container
 * onImage and onThumb functions lets you customize the behaviours of the images on the site
 *
 * Tested in Safari 3, Firefox 2, MSIE 6, MSIE 7, Opera 9
 * 
 * Version 1.0
 * Februari 21, 2008
 *
 * Copyright (c) 2008 David Hellsing (http://monc.se)
 * Licensed under the GPL licenses.
 * http://www.gnu.org/licenses/gpl.txt
 **/

;(function($){

var $$;


/**
 * 
 * @desc Convert images from a simple html <ul> into a thumbnail gallery
 * @author David Hellsing
 * @version 1.0
 *
 * @name Galleria
 * @type jQuery
 *
 * @cat plugins/Media
 * 
 * @example $('ul.gallery').galleria({options});
 * @desc Create a a gallery from an unordered list of images with thumbnails
 * @options
 *   insert:   (selector string) by default, Galleria will create a container div before your ul that holds the image.
 *             You can, however, specify a selector where the image will be placed instead (f.ex '#main_img')
 *   history:  Boolean for setting the history object in action with enabled back button, bookmarking etc.
 *   onImage:  (function) a function that gets fired when the image is displayed and brings the jQuery image object.
 *             You can use it to add click functionality and effects.
 *             f.ex onImage(image) { image.css('display','none').fadeIn(); } will fadeIn each image that is displayed
 *   onThumb:  (function) a function that gets fired when the thumbnail is displayed and brings the jQuery thumb object.
 *             Works the same as onImage except it targets the thumbnail after it's loaded.
 *
**/

$$ = $.fn.galleria = function($options) {
	
	// check for basic CSS support
	if (!$$.hasCSS()) { return false; }
	
	// init the modified history object
	$.historyInit($$.onPageLoad);
	
	// set default options
	var $defaults = {
		insert      : '.galleria_container',
		history     : true,
		clickNext   : true,
		onImage     : function(image,caption,thumb) {},
		onThumb     : function(thumb) {}
	};
	

	// extend the options
	var $opts = $.extend($defaults, $options);
	
	// bring the options to the galleria object
	for (var i in $opts) {
		$.galleria[i]  = $opts[i];
	}
	
	// if no insert selector, create a new division and insert it before the ul
	var _insert = ( $($opts.insert).is($opts.insert) ) ? 
		$($opts.insert) : 
		jQuery(document.createElement('div')).insertBefore(this);
		
	// create a wrapping div for the image
	var _div = $(document.createElement('div')).addClass('galleria_wrapper');
	
	// inject the wrapper in in the insert selector
	_insert.addClass('galleria_container').append(_div);
	
	//-------------
	
	return this.each(function(){
		
		// add the Galleria class
		$(this).addClass('galleria');
		
		// loop through list
		$(this).children('li').each(function(i) {
			
			// bring the scope
			var _container = $(this);
			
			// build element specific options
			var _o = $.meta ? $.extend({}, $opts, _container.data()) : $opts;
			
			// remove the clickNext if image is only child
			_o.clickNext = $(this).is(':only-child') ? false : _o.clickNext;
			$.galleria.clickNext = _o.clickNext;
			
			// try to fetch an anchor
			var _a = $(this).find('a').is('a') ? $(this).find('a') : false;
			
			// reference the original image as a variable and hide it
			var _img = $(this).children('img').css('display','none');
			
			// extract the original source
			var _src = _a ? _a.attr('href') : _img.attr('src');
			
			// find a title
			var _title = _a ? _a.attr('title') : _img.attr('title');
			
			// create loader image
			var _loader = new Image();
			
			// check url and activate container if match
			if (_o.history && (window.location.hash && window.location.hash.replace(/\#/,'') == _src)) {
				_container.siblings('.active').removeClass('active');
				_container.addClass('active');
			}
		
			// begin loader
			$(_loader).load(function () {
				
				// try to bring the alt
				$(this).attr('alt',_img.attr('alt'));
				
				//-----------------------------------------------------------------
				// the image is loaded, let's create the thumbnail
				
				var _thumb = _a ? 
					_a.find('img').addClass('thumb noscale').css('display','none') :
					_img.clone(true).addClass('thumb').css('display','none');
				
				if (_a) { _a.replaceWith(_thumb); }
				
				if (!_thumb.hasClass('noscale')) { // scaled tumbnails!
					var w = Math.ceil( _img.width() / _img.height() * _container.height() );
					var h = Math.ceil( _img.height() / _img.width() * _container.width() );
					if (w < h) {
						_thumb.css({ height: 'auto', width: _container.width(), marginTop: -(h-_container.height())/2 });
					} else {
						_thumb.css({ width: 'auto', height: _container.height(), marginLeft: -(w-_container.width())/2 });
					}
				} else { // Center thumbnails.
					// a tiny timer fixed the width/height
					window.setTimeout(function() {
						_thumb.css({
							marginLeft: -( _thumb.width() - _container.width() )/2, 
							marginTop:  -( _thumb.height() - _container.height() )/2
						});
					}, 1);
				}
				
				// add the rel attribute
				_thumb.attr('rel',_src);
				
				// add the title attribute
				_thumb.attr('title',_title);
				
				// add the click functionality to the _thumb
				_thumb.click(function() {
					$.galleria.activate(_src);
				});
				
				// hover classes for IE6
				_thumb.hover(
					function() { $(this).addClass('hover'); },
					function() { $(this).removeClass('hover'); }
				);
				_container.hover(
					function() { _container.addClass('hover'); },
					function() { _container.removeClass('hover'); }
				);

				// prepend the thumbnail in the container
				_container.prepend(_thumb);
				
				// show the thumbnail
				_thumb.css('display','block');
				
				// call the onThumb function
				_o.onThumb(jQuery(_thumb));
				
				// check active class and activate image if match
				if (_container.hasClass('active')) {
					$.galleria.activate(_src);
				}
				
				//-----------------------------------------------------------------
				
				// finally delete the original image
				_img.remove();
				
			}).error(function () {
				
				// Error handling
			    _container.html('<span class="error" style="color:red">Error loading image: '+_src+'</span>');
			
			}).attr('src', _src);
		});
	});
};

/**
 *
 * @name NextSelector
 *
 * @desc Returns the sibling sibling, or the first one
 *
**/

$$.nextSelector = function(selector) {
	return $(selector).is(':last-child') ?
		   $(selector).siblings(':first-child') :
    	   $(selector).next();
    	   
};

/**
 *
 * @name previousSelector
 *
 * @desc Returns the previous sibling, or the last one
 *
**/

$$.previousSelector = function(selector) {
	return $(selector).is(':first-child') ?
		   $(selector).siblings(':last-child') :
    	   $(selector).prev();
    	   
};

/**
 *
 * @name hasCSS
 *
 * @desc Checks for CSS support and returns a boolean value
 *
**/

$$.hasCSS = function()  {
	$('body').append(
		$(document.createElement('div')).attr('id','css_test')
		.css({ width:'1px', height:'1px', display:'none' })
	);
	var _v = ($('#css_test').width() != 1) ? false : true;
	$('#css_test').remove();
	return _v;
};

/**
 *
 * @name onPageLoad
 *
 * @desc The function that displays the image and alters the active classes
 *
 * Note: This function gets called when:
 * 1. after calling $.historyInit();
 * 2. after calling $.historyLoad();
 * 3. after pushing "Go Back" button of a browser
 *
**/

$$.onPageLoad = function(_src) {	
	
	// get the wrapper
	var _wrapper = $('.galleria_wrapper');
	
	// get the thumb
	var _thumb = $('.galleria img[@rel="'+_src+'"]');
	
	if (_src) {
		
		// new hash location
		if ($.galleria.history) {
			window.location = window.location.href.replace(/\#.*/,'') + '#' + _src;
		}
		
		// alter the active classes
		_thumb.parents('li').siblings('.active').removeClass('active');
		_thumb.parents('li').addClass('active');
	
		// define a new image
		var _img   = $(new Image()).attr('src',_src).addClass('replaced');

		// define a new caption
		var _span = $(document.createElement('span')).addClass('caption');
		if(!_thumb.attr('title')) {
			_span.css('display','none');
		} else {
			_span.text(_thumb.attr('title'));
		}

		// define a div container for the image
		var _div = $(document.createElement('div')).addClass('image-container')
		_div.append(_img);
		_div.append(_span);

		// empty the wrapper and insert the new image
		_wrapper.empty().append(_div);

		// fire the onImage function to customize the loaded image's features
		$.galleria.onImage(_img,_span,_thumb);
		
		// add clickable image helper
		if($.galleria.clickNext) {
			_img.css('cursor','pointer').click(function() { $.galleria.next(); })
		}
		
	} else {
		
		// clean up the container if none are active
		_wrapper.siblings().andSelf().empty();
		
		// remove active classes
		$('.galleria li.active').removeClass('active');
	}

	// place the source in the galleria.current variable
	$.galleria.current = _src;
	
}

/**
 *
 * @name jQuery.galleria
 *
 * @desc The global galleria object holds four constant variables and four public methods:
 *       $.galleria.history = a boolean for setting the history object in action with named URLs
 *       $.galleria.current = is the current source that's being viewed.
 *       $.galleria.clickNext = boolean helper for adding a clickable image that leads to the next one in line
 *       $.galleria.next() = displays the next image in line, returns to first image after the last.
 *       $.galleria.prev() = displays the previous image in line, returns to last image after the first.
 *       $.galleria.activate(_src) = displays an image from _src in the galleria container.
 *       $.galleria.onImage(image,caption) = gets fired when the image is displayed.
 *
**/

$.extend({galleria : {
	current : '',
	onImage : function(){},
	activate : function(_src) { 
		if ($.galleria.history) {
			$.historyLoad(_src);
		} else {
			$$.onPageLoad(_src);
		}
	},
	next : function() {
		var _next = $($$.nextSelector($('.galleria img[@rel="'+$.galleria.current+'"]').parents('li'))).find('img').attr('rel');
		$.galleria.activate(_next);
	},
	prev : function() {
		var _prev = $($$.previousSelector($('.galleria img[@rel="'+$.galleria.current+'"]').parents('li'))).find('img').attr('rel');
		$.galleria.activate(_prev);
	}
}
});

})(jQuery);

/*
 * jQuery history plugin
 * 
 * sample page: http://www.mikage.to/jquery/jquery_history.html
 *
 * Copyright (c) 2006-2009 Taku Sano (Mikage Sawatari)
 * Licensed under the MIT License:
 *   http://www.opensource.org/licenses/mit-license.php
 *
 * Modified by Lincoln Cooper to add Safari support and only call the callback once during initialization
 * for msie when no initial hash supplied.
 */

jQuery.extend({
    historyCurrentHash: undefined,
    historyCallback: undefined,
    historyIframeSrc: undefined,
    historyNeedIframe: jQuery.browser.msie && (jQuery.browser.version < 8 || document.documentMode < 8),
    
    historyInit: function(callback, src){
        jQuery.historyCallback = callback;
        if (src) jQuery.historyIframeSrc = src;
        var current_hash = location.hash.replace(/\?.*$/, '');
        
        jQuery.historyCurrentHash = current_hash;
        if (jQuery.historyNeedIframe) {
            // To stop the callback firing twice during initilization if no hash present
            if (jQuery.historyCurrentHash == '') {
                jQuery.historyCurrentHash = '#';
            }
        
            // add hidden iframe for IE
            jQuery("body").prepend('<iframe id="jQuery_history" style="display: none;"'+
                ' src="javascript:false;"></iframe>'
            );
            var ihistory = jQuery("#jQuery_history")[0];
            var iframe = ihistory.contentWindow.document;
            iframe.open();
            iframe.close();
            iframe.location.hash = current_hash;
        }
        else if (jQuery.browser.safari) {
            // etablish back/forward stacks
            jQuery.historyBackStack = [];
            jQuery.historyBackStack.length = history.length;
            jQuery.historyForwardStack = [];
            jQuery.lastHistoryLength = history.length;
            
            jQuery.isFirst = true;
        }
        if(current_hash)
            jQuery.historyCallback(current_hash.replace(/^#/, ''));
        setInterval(jQuery.historyCheck, 100);
    },
    
    historyAddHistory: function(hash) {
        // This makes the looping function do something
        jQuery.historyBackStack.push(hash);
        
        jQuery.historyForwardStack.length = 0; // clear forwardStack (true click occured)
        this.isFirst = true;
    },
    
    historyCheck: function(){
        if (jQuery.historyNeedIframe) {
            // On IE, check for location.hash of iframe
            var ihistory = jQuery("#jQuery_history")[0];
            var iframe = ihistory.contentDocument || ihistory.contentWindow.document;
            var current_hash = iframe.location.hash.replace(/\?.*$/, '');
            if(current_hash != jQuery.historyCurrentHash) {
            
                location.hash = current_hash;
                jQuery.historyCurrentHash = current_hash;
                jQuery.historyCallback(current_hash.replace(/^#/, ''));
                
            }
        } else if (jQuery.browser.safari) {
            if(jQuery.lastHistoryLength == history.length && jQuery.historyBackStack.length > jQuery.lastHistoryLength) {
                jQuery.historyBackStack.shift();
            }
            if (!jQuery.dontCheck) {
                var historyDelta = history.length - jQuery.historyBackStack.length;
                jQuery.lastHistoryLength = history.length;
                
                if (historyDelta) { // back or forward button has been pushed
                    jQuery.isFirst = false;
                    if (historyDelta < 0) { // back button has been pushed
                        // move items to forward stack
                        for (var i = 0; i < Math.abs(historyDelta); i++) jQuery.historyForwardStack.unshift(jQuery.historyBackStack.pop());
                    } else { // forward button has been pushed
                        // move items to back stack
                        for (var i = 0; i < historyDelta; i++) jQuery.historyBackStack.push(jQuery.historyForwardStack.shift());
                    }
                    var cachedHash = jQuery.historyBackStack[jQuery.historyBackStack.length - 1];
                    if (cachedHash != undefined) {
                        jQuery.historyCurrentHash = location.hash.replace(/\?.*$/, '');
                        jQuery.historyCallback(cachedHash);
                    }
                } else if (jQuery.historyBackStack[jQuery.historyBackStack.length - 1] == undefined && !jQuery.isFirst) {
                    // back button has been pushed to beginning and URL already pointed to hash (e.g. a bookmark)
                    // document.URL doesn't change in Safari
                    if (location.hash) {
                        var current_hash = location.hash;
                        jQuery.historyCallback(location.hash.replace(/^#/, ''));
                    } else {
                        var current_hash = '';
                        jQuery.historyCallback('');
                    }
                    jQuery.isFirst = true;
                }
            }
        } else {
            // otherwise, check for location.hash
            var current_hash = location.hash.replace(/\?.*$/, '');
            if(current_hash != jQuery.historyCurrentHash) {
                jQuery.historyCurrentHash = current_hash;
                jQuery.historyCallback(current_hash.replace(/^#/, ''));
            }
        }
    },
    historyLoad: function(hash){
        var newhash;
        hash = decodeURIComponent(hash.replace(/\?.*$/, ''));
        
        if (jQuery.browser.safari) {
            newhash = hash;
        }
        else {
            newhash = '#' + hash;
            location.hash = newhash;
        }
        jQuery.historyCurrentHash = newhash;
        
        if (jQuery.historyNeedIframe) {
            var ihistory = jQuery("#jQuery_history")[0];
            var iframe = ihistory.contentWindow.document;
            iframe.open();
            iframe.close();
            iframe.location.hash = newhash;
            jQuery.lastHistoryLength = history.length;
            jQuery.historyCallback(hash);
        }
        else if (jQuery.browser.safari) {
            jQuery.dontCheck = true;
            // Manually keep track of the history values for Safari
            this.historyAddHistory(hash);
            
            // Wait a while before allowing checking so that Safari has time to update the "history" object
            // correctly (otherwise the check loop would detect a false change in hash).
            var fn = function() {jQuery.dontCheck = false;};
            window.setTimeout(fn, 200);
            jQuery.historyCallback(hash);
            // N.B. "location.hash=" must be the last line of code for Safari as execution stops afterwards.
            //      By explicitly using the "location.hash" command (instead of using a variable set to "location.hash") the
            //      URL in the browser and the "history" object are both updated correctly.
            location.hash = newhash;
        }
        else {
          jQuery.historyCallback(hash);
        }
    }
});

