<?php


/// Adam Borecki's Batch Rename Script


$contents = print_r($argv,true);

// current directory: $argv[0]

$list_src = @$argv[1];

function alert($msg){
	$msg = "- Adam Borecki's Batch Rename Droplet -\n      adamborecki.com/batchrename\n\n".$msg;
	passthru("osascript -e 'tell application \"Finder\" to activate';osascript -e 'tell application \"Finder\" to display alert \"".str_replace(array("'","\""),array("’","\\\""),$msg)."\"'");
	die;
}

if(!$list_src)
	alert("Missing or invalid '\$list_src' variable. Please click and drag into the droplet (or if using as command line, please pass as the first argument).");

$contents = @file_get_contents($list_src);

if(!$contents)
	alert("Unable to read to contents of $list_src.\n\nPlease drag a plain text (.txt) file into the droplet.");

if(strpos($contents,"{\\rtf") !== false)
	alert("Error: Incompatible format: .RTF\n\nYou dragged in a 'rich text' file. Only 'plain text' is supported.\n\nTo fix this:\nIf you're using TextEdit, you can convert to a plain text file:\n\tShift + Command + T\n\nPlease try again, but use a plain text file (.txt) instead.");

$contents = str_replace("\r\n","\n", $contents);
$contents = str_replace("\n\r","\n", $contents);
$contents = str_replace("\r","\n", $contents);
$lines = explode("\n",$contents);

$rename_key = array();

$config = array(
	"folderPrefix" => "",
);

// from this point on, we'll save this in an array 
$errors = array();
$warnings = array();
foreach($lines as $lineNum => $line) {
	if($line == "")
		continue;
	$line = trim($line);
	if($line == "" || substr($line,0,1) == ";") {
		continue;
	}
	if( strpos($line,"=")  ) {
		list($k,$v) = explode("=",$line);
		$k = trim($k);
		$v = trim($v);
		switch( strtolower($k) ) {
			case "folderprefix":
				$config['folderPrefix'] = $v;
				break;
			default:
				alert("Unknown configuration option '$k' on line $lineNum.\n\nNote that the equals sign = is a special character in Adam Borecki's Rename Droplet.\n\nIf you try a filename with an equals sign =, you'll get this error message.");
		}
	}
	else {
		$firstspace = strpos($line," ");
		if($firstspace === false)
			$warnings[] = "Line $lineNum did not have a space, so it was ignored and no shortcode was created. (Line: $line)";
		else {
			$shortcode = substr( $line,0, $firstspace );
			if( isset($rename_key[$shortcode]) ) {
				$warnings[] = "Duplicate shortcode '$shortcode' on line $lineNum will be ignored. This is probably a problem";
			}
			else {
				$rename_key[ $shortcode ] = $line;
				if(strlen($line) > 255)
					$warnings[] = "Line $lineNum is longer than 255 characters, which might cause issues on Windows computers!";
				$windowsWarningChars = array("<",">","\"","\\","|","?","*");
				foreach($windowsWarningChars as $windowsWarningChar ){
					if( strpos($line, $windowsWarningChar) !== false  ){
						if($windowsWarningChar == "\\")
							$windowsWarningChar = "\\\\";
						$warnings[] = ("Line $lineNum contained the following special character: $windowsWarningChar, which might problems on Windows computers.");
					}
				}
			}
		}
	}
}

if(!$rename_key){
	alert("Unable to create a rename key. Please make sure that you're dragging in a simple, plain text file (.txt) with proper formatting.\\n\\nIf you dragged a .txt file in, make sure that it is properly formatted and that the syntax is correct.");
}
else {
	$path = pathinfo( $list_src , PATHINFO_DIRNAME);
	if(substr($path,-1) != "/")
		$path .= "/";
	
	/*
	exec("osascript -e 'display dialog \"(recommended)\nDo you want to run 'renameSpecial'? DownMix and Surround will have DwnMix and SRND appended, and surround files will sort themselves into folders.\\n\\n"
		."For example:\\n"
		."Surround\\n"
			."\\t- 01 Beethoven - I. mvt one.L.wav\\n"
			."\\t- 02 Beethoven - II. mvt two.L.wav\\n"
			."\\t- ...\\n"
		."\\nwill become:\\n\\n"
		."Surround\n"
			."\t01 Beethoven - I. mvt one SRND\n"
				."\\t\\t- 01 Beethoven - I. one SRND.L.wav\n"
				."\\t\\t- 01 Beethoven - I. one SRND.C.wav\n"
				."\t\t- ... \n"
			."\t02 Beethoven - II. mvt two SRND\n"
				."\\t\\t- 01 Beethoven - II. two SRND.L.wav\n"
				."\\t\\t- 01 Beethoven - II. two SRND.C.wav\n"
				."\t\t- ... "
		."\"'"
		, $testoutput);
	$config['renameSpecial'] = $testoutput[0] == "button returned:OK" ? true : false;
	*/
	$config['renameSurround'] = true;
	$config['renameDownmix'] = true;
	
	// let's put in the folder prefix
	if($config['folderPrefix']) {
		$contents = scandir( $path );
		$folderPrefix_length = strlen($config['folderPrefix']);
		foreach($contents as $file) {
			if(substr($file,0,1) == ".")
				continue;
			if(is_dir($path.$file) && substr($file,0,$folderPrefix_length) != $config['folderPrefix']  ) {
				rename( $path.$file, $path.$config['folderPrefix']." $file");
			}
		}
		sleep(2); // for some reason this helps...
		clearstatcache();
	}

	$output = renameInFolder( $path, $rename_key, 0, $config );
	$errors = array_merge($errors,$output['errors']);
	$warnings = array_merge($warnings,$output['warnings']);

	$msg = "Renaming finished.\n\n\t".count($output['results'])." file(s) renamed.\n\nError(s): ".count($errors)."\nWarning(s): ".count($warnings)."\n";
	
	if($errors){ 
		$msg .= "\n";
		foreach($errors as $err) {
			$msg .= "  • [error] $err\n";
		}
	}
	if($warnings) {
		$msg .= "\n";
		foreach($warnings as $warn) {
			$msg .= "  • [warning] $warn\n";
		}
	}
	
	if($errors || $warnings) {
		file_put_contents($path."(Batch Output Warnings, Errors, and Results).txt","- Adam Borecki's Batch Rename Droplet -\n\n".date('r')."]\n\n"
			."ERROR(S): ".print_r($errors,true)
			."WARNING(S): ".print_r($warnings,true)
			."RESULTS: ".print_r($output['results'],true)
			
			);
		$msg .= "\n\nThis has been saved to a new text file in the same directory.";
	}
	
	alert($msg);
}


function renameInFolder($folder,$rename_key, $recursion = 0, $config){
	$errors = array();
	$warnings = array();
	$results = array();
	if($recursion > 2){
		$warnings[] = "Too much recursion! (Over 2 levels of subdirectories...) This is probably a programming error, check with Adam if you actually need more subdirectories";
	}
	else {
		if(substr($folder,-1)!="/"){
			$folder .= "/";
		}
		// we'll want to know the top level folder (topfolder) in advance
		$folderparts = explode("/",$folder);
		$topfolder = $folderparts[ count($folderparts)-2 ];
		if( substr($topfolder,-1) != "/")
			$topfolder .= "/";
		$topfolderlowercase = strtolower($topfolder);
		
		// let's take a look at the contents
		$contents = scandir($folder);		
		foreach($contents as $file) {
			if(substr($file,0,1) == "."){
				continue;
			}
			
			// handle subfolders? (recursion)
			if(is_dir($folder.$file)) {
				$output = renameInFolder( $folder.$file, $rename_key, $recursion + 1, $config);
				$errors = array_merge($errors, $output['errors']);
				$warnings = array_merge($errors, $output['warnings']);
				$results = array_merge($errors, $output['results']);
			} else {
				// parse this file
				$spacepos = strpos($file," ");
				$periodpos = strpos($file,".");
				if(!$periodpos) {
					$errors[] = "The file $folder$file did not have a period in it, which means the script can't figure out what the extension is. That's a bummer.";
				}
				else {
					$this_shortcode = (
						($spacepos !== false && $spacepos < $periodpos)
							? substr($file,0,$spacepos)
							: substr($file,0,$periodpos)
					);
					if(isset($rename_key[$this_shortcode])) {
						// let's rename it!
						$newfolder = "";
						$newbase = sanitizeFilename($rename_key[$this_shortcode]); // replace the dangerous things from the new rename line
						$appendtext = "";

						
						// process rename surround differently!
						if($config['renameSurround']) {
							if( $recursion == 1 && isSurroundFolder($topfolderlowercase) ) {
								$newfolder = sanitizeFilename($rename_key[$this_shortcode]." SRND")."/";
								if(!file_exists($folder.$newfolder))
									mkdir($folder.$newfolder);
							}
							if( isSurroundFolder($topfolderlowercase) ) {
								$appendtext = " SRND";
							}
						}
						if($config['renameDownmix']) {
							if( isDownmixFolder($topfolderlowercase) ) {
								$appendtext = " DwnMx";
							}
						}
						
						// we need to get the extension and any "goop" in front of it (such as .L.wav)
						// basically, anything without a space
						$splitbyperiods = explode(".", str_replace($rename_key[$this_shortcode],"", $file) );
						$ext_and_goop = "";
						for($i = count($splitbyperiods)-1;$i >=0;$i--){
							$part = $splitbyperiods[ $i ];
							if(!$part)
								continue;
							if( strpos($part," ") === false && $part != $this_shortcode) {
								$ext_and_goop = ".$part".$ext_and_goop;
							}
						}

						$newname = $newfolder . $newbase . $appendtext . $ext_and_goop;

						if("$folder$file" != "$folder$newname") {
							$results[] = "rename('$folder$file','$folder$newname')";
							rename("$folder$file","$folder$newname");
						}
					}
				}
			}
		}
	}
	return array('errors'=>$errors,'warnings'=>$warnings,'results'=>$results);
}

function isSurroundFolder($topfolderlowercase) {
	return strpos($topfolderlowercase,"surround") !== false || strpos($topfolderlowercase,"surr") !== false || strpos($topfolderlowercase," srnd") !== false;
}

function isDownmixFolder($topfolderlowercase) {
	return strpos($topfolderlowercase,"dwnmix") !== false || strpos($topfolderlowercase,"downmix") !== false || strpos($topfolderlowercase,"dwnmix") !== false;
}


function strposa($haystack, $needles=array(), $offset=0) {
        $chr = array();
        foreach($needles as $needle) {
                $res = strpos($haystack, $needle, $offset);
                if ($res !== false) $chr[$needle] = $res;
        }
        if(empty($chr)) return false;
        return min($chr);
}

function sanitizeFilename($input) {
//	return str_replace( array("/",":",""), array("∕","﹕","") ,$input); // small colon, not as nice
	return str_replace( array("/",":",""), array("∕","：","") ,$input);
}