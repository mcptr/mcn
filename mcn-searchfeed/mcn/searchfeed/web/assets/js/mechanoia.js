(function($) {
	"use strict";

	class Event
	{
		constructor(e)
		{
			this.event = e;
		}

		target()
		{
			return $(this.event.target);
		}

		data()
		{
			return this.target().attr("data-event-id");
		}

		name()
		{
			return this.target().attr("data-event");
		}
	}
	
	class EventSystem
	{
		constructor()
		{
			this.subscriptions = {};
		}

		trigger(e)
		{
			var name = e.name();
			console.info("Trigger event:", name, e);
			this.subscriptions[name].forEach(function(func, idx) {
				console.info("TRIG", e, func);
				func(e);
			});
			return false;
		}

		on(name, callback)
		{
			console.info("Subscribe event:", name);
			if(this.subscriptions[name] === undefined) {
				this.subscriptions[name] = [];
			}
			this.subscriptions[name].push(callback);
		}
	};

	class Mechanoia {
		constructor()
		{
			console.log("INIT Mechanoia");
			this.ev = new EventSystem();
			this.event_data = {};
			this.setup_events();
		}

		api_call(url)
		{
			$.ajax(url).fail(console.error).done(console.log);
		}
		
		setup_events()
		{
			this.ev.on("click/url/tag", (e) => {
				console.log("EV", e.data());
				let d = JSON.parse('"' + e.data() + '"');
				console.log("DDDDDDDD", d);
				
				// let url = `/url/tag?url=${d.url}&tag=${d.tag}`;
				// this.api_call(url);
				// e.target().remove();
			});
		}
	}

	var app = new Mechanoia();
	window.app = app;
	window.event_data = {};

	$(".event-emitter.click").click(function(e) {
		app.ev.trigger(new Event(e));
	});
})(jQuery);
