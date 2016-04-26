/**
 * jspsych-attr-custom
 * Linjie Li
 *
 * plugin for displaying a stimulus and getting a likert response
 *
 * documentation: docs.jspsych.org
 *
 **/

(function($) {
	jsPsych.attr_custom = (function() {

		var plugin = {};

		plugin.create = function(params) {

			params = jsPsych.pluginAPI.enforceArray(params, ['data']);

			var trials = new Array(params.stimuli.length);
			for (var i = 0; i < trials.length; i++) {
				trials[i] = {};
				trials[i].number = (i+1).toString();
				trials[i].total = trials.length.toString();
				trials[i].totalPhase = (typeof params.totalPhase === 'undefined') ? "4" : params.totalPhase.toString();
				trials[i].text = (typeof params.text === 'undefined') ? "" : params.text;
				trials[i].phase = (typeof params.phase === 'undefined') ? "" : params.phase.toString();
				trials[i].trial_num = (typeof params.trial_num === 'undefined') ? "" : params.trial_num.toString();
		        trials[i].set_num = (typeof params.set_num === 'undefined') ? "" : params.set_num.toString();
		        trials[i].a_path = params.stimuli[i];
				// trials[i].choices = params.choices || [];
				trials[i].show_ticks = (typeof params.show_ticks === 'undefined') ? false : params.show_ticks;
				trials[i].response_ends_trial = (typeof params.response_ends_trial === 'undefined') ? true : params.response_ends_trial;
				// timing parameters
				trials[i].timing_stim = params.timing_stim || -1; // if -1, then show indefinitely
				trials[i].timing_response = params.timing_response || -1; // if -1, then wait for response forever
				// optional parameters
				trials[i].is_html = (typeof params.is_html === 'undefined') ? false : params.is_html;
				trials[i].prompt = (typeof params.prompt === 'undefined') ? "" : params.prompt;
			}
			return trials;
		};


		var attr_trial_complete = false;
		plugin.trial = function(display_element, trial) {
			// this array holds handlers from setTimeout calls
			// that need to be cleared if the trial ends early
			var setTimeoutHandlers = [];
			dotrial();
			function dotrial() {
				// if any trial variables are functions
				// this evaluates the function and replaces
				// it with the output of the function
		        trial = jsPsych.pluginAPI.evaluateFunctionParameters(trial);
		        display_element.html(trial.text);
		        if (trial.phase.length >= 1){
		          display_element.append('<div> <p> <span class="emp">Phase:</span> ' + trial.phase + ' of'+trial.totalPhase+'</p> <p><span class="emp">Progress:</span> '+trial.number +' of '+trial.total+'</p></div>');
		        }
		        
		        // display stimulus
				if (!trial.is_html) {
					display_element.append($('<img>', {
						src: trial.a_path,
						id: 'jspsych-single-stim-stimulus'
					}));
				} else {
					display_element.append($('<div>', {
						html: trial.a_path,
						id: 'jspsych-single-stim-stimulus'
					}));
				}

		        setTimeoutHandlers.push(setTimeout(function() {
		          showSecondStim();
		        }, 0));
		    }
			
		    function key_listener(){
		        $(window).unbind('keypress', key_listener);
		        $('.text-warning').html('Continuing...');
		        setTimeout(function(){
		          display_element.empty();
		          dotrial();
		        }, 1000);
		    }

		    function showWarningScreen() {
		        display_element.empty();
		        display_element.append($('<p>', {
		          "class": 'text-warning',
		          "html": 'You have not responded for a long time. Press any key to continue.'
		        }));
		        $(window).keypress(key_listener);
		    }

		    function show_response_slider(display_element, trial) {

		        var startTime = (new Date()).getTime();
		        display_element.append('<table id="likert_scale" style="font-size:25px"> <tbody> <tr> <td style="text-align: center; width: 50px;font-size:25px">Maximally <br>Unattractive</td> <td class="radio_scale" > <form action="" style="text-align: center;"> <input id="scale_value" type="radio" name="scale_value" value="1"> <input id="scale_value" type="radio" name="scale_value" value="2"> <input id="scale_value" type="radio" name="scale_value" value="3"> <input id="scale_value" type="radio" name="scale_value" value="4"> <input id="scale_value" type="radio" name="scale_value" value="5"> <input id="scale_value" type="radio" name="scale_value" value="6"> <input id="scale_value" type="radio" name="scale_value" value="7"> <input id="scale_value" type="radio" name="scale_value" value="8"> <input id="scale_value" type="radio" name="scale_value" value="9"> </form> </td> <td style="text-align: center; width: 50px;font-size:25px">Maximally <br>Attractive</td> </tr> <tr> <td style="text-align: center; width: 75px;font-size:25px"> </td> <td class="radio_scale"> <form action="" style="text-align: center; margin-left: 5.6%;"> <li id="scalelabels"> 1 </li> <li id="scalelabels"> 2 </li> <li id="scalelabels"> 3 </li> <li id="scalelabels"> 4 </li> <li id="scalelabels"> 5 </li> <li id="scalelabels"> 6 </li> <li id="scalelabels"> 7 </li> <li id="scalelabels"> 8 </li> <li id="scalelabels"> 9 </li> </form> </td> <td style="text-align: center; width: 75px;font-size:25px"> </td> </tr></tbody> </table>');
        
		        $("input[name='scale_value']").change(function(){
		          // get the attractiveness score and end the trial
		          var score = getValue('scale_value');
		          var score_valid = ((parseInt(score)>=1) && (parseInt(score)<=9));
		          //console.log(score_valid);
		          if ( score_valid ){
		            setTimeout(function(){
		              wrapup_trial();
		            }, 500);
		          }
		        });
        
        
	        function getValue(name) {
	          var rbs = document.getElementsByName(name);
	          var iLen=rbs.length;
	          var value = [];
	          for (var i=0;  i < iLen; i++) {
	            if (rbs[i].checked) {
	              value.push(rbs[i].value);
	            }
	          }
	          return value;
	        }

			//show prompt if there is one
			if (trial.prompt !== "") {
				display_element.append(trial.prompt);
			}

			// function to end trial when it is time // store response
			function wrapup_trial(){
	          var score = getValue('scale_value');
	          var endTime = (new Date()).getTime();
	          var response_time = endTime - startTime;

	          // kill any remaining setTimeout handlers
	          for (var i = 0; i < setTimeoutHandlers.length; i++) {
	            clearTimeout(setTimeoutHandlers[i]);
	          }

	          console.log(score);
	          jsPsych.data.write($.extend({}, {
	            "attr_score": score,
	            "rt": response_time,
	            "stimulus": JSON.stringify([trial.a_path]),
	            "type": trial.trial_num,
	            "set": trial.set_num
	          }, trial.data));
	          // goto next trial in block
	          display_element.html('');
	          if (trial.timing_post_trial > 0) {
	            setTimeout(function() {
	              jsPsych.finishTrial();
	            }, trial.timing_post_trial);
		      } else {
	            jsPsych.finishTrial();
	          }
        
	        } // end of function wrapup_trial
		  }
		};

		return plugin;
	})();
})(jQuery);
