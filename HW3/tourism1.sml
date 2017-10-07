(* Reduce output message*)
Control.Print.out := {say=fn _=>(), flush=fn()=>()};

open String Int OS.Process CommandLine;

val infp = case CommandLine.arguments () of [fp] => fp | _ => raise Fail "Input file path!";

(* Parse line from file*)
fun readlist (infile : string) = 
	let 
		val ins = TextIO.openIn infile 

		fun loop ins = 
			case TextIO.inputLine ins of 
				SOME line => line :: loop ins 
				| NONE => [] 
	in 
		loop ins before TextIO.closeIn ins 
	end ;                        

(* All lines in file*)                            
val parse_string = readlist(infp);

fun parse_people ([]) = NONE 
	| parse_people(h::t) = 
        if isPrefix "people(" h then fromString(substring(h,size("people("), 1) )  
		else parse_people(t);
    
fun parse_loc ([]) = NONE
	| parse_loc(h::t) = 
		if isPrefix "locations(" h then fromString(substring(h,size("locations("), 1) )  
	else parse_loc(t);

fun parse_pref ([]) = NONE 
	| parse_pref(h::t) = 
		if isPrefix "preferences(" h then fromString(substring(h, size("preferences("), 1) )  
		else parse_pref(t);

fun str_to_int_list(h) = 
		tokens (fn c => c = #",") (substring(h, size("order("), size(h)-size("order().\n") ));

fun parse_order ([]) = [] 
	| parse_order(h::t) = 
		if isPrefix "order(" h then  foldr (fn (x, y) => Option.valOf (Int.fromString x) :: y ) [] (str_to_int_list(h)) :: parse_order(t) 
		else parse_order(t);

val SOME people = parse_people(parse_string)
val SOME locations = parse_loc(parse_string)
val SOME preferences = parse_pref(parse_string)
val orders = parse_order(parse_string)

fun list2tuple([]) = []
	| list2tuple(h::t) =
	let
		val tup = (List.hd(h), List.nth(h,1), List.last(h))
	in
		tup :: list2tuple(t)
	end;

fun tuple2list([]) = []
	| tuple2list(L:(int*int*int) list) = 
		let
			val lis = [#1 (List.hd(L)), #2 (List.hd(L)), #3 (List.hd(L))] 
		in
			lis :: tuple2list(List.tl(L))
		end;

val orders_tuple = list2tuple(orders);

(* Add the behind place to every sets which has the front place in that set*)
fun add_behind(old_map:IntListSet.set IntListMap.map, front, behind) = 
	 (* try to find front in every set in map item x*)
	IntListMap.map (fn x => 
						if IntListSet.member(x, front) 
							then IntListSet.add(x, behind)
						else x
					) old_map

(* Insert a new map if the front place doesn't exist in the map list, 
	the map key is front place, map value is a set contains all place behind the #key place *)
fun add_new(old_map:IntListSet.set IntListMap.map, front, behind) =
	let 
		val front_set = IntListMap.find(old_map, front) 
	in 
		if Option.isSome(front_set) then 
			IntListMap.insert(old_map, front, IntListSet.add(Option.valOf(front_set), behind))   
		else IntListMap.insert(old_map, front, (IntListSet.add(IntListSet.empty, behind)) )
	end;

(* If the new behind place is already exist as a key in the map, all place in that mapped set 
	must be add into the corresponding front place's set*)
fun union_after_behind(old_map:IntListSet.set IntListMap.map, front, behind) =
	let
		val front_set = Option.valOf(IntListMap.find(old_map, front)) 
		val behind_set = IntListMap.find(old_map, behind)
	in 
		if Option.isSome(behind_set) then 
			IntListMap.insert(old_map, front, IntListSet.union(front_set, Option.valOf(behind_set)))
		else old_map
	end;   

(* Update the map list target_ind th element with new_val*)	
fun update_list(L:'a list, target_ind, new_val:'a):'a list = 
    let 
        val front = List.take(L, target_ind)
        val left = List.drop(L, target_ind+1)
    in
        front @ (new_val :: left)
    end;

(* Generate map contains people and their set*)
fun generate_order_map(orders:IntListSet.set IntListMap.map list, []) = orders
	| generate_order_map(orders:IntListSet.set IntListMap.map list, order::remain) =
	(* check if map list contains this person's order, if not append one*)
	if List.length(orders) < hd(order) then
		generate_order_map(orders @ [IntListMap.empty], order::remain) 
	else
		let 
			val person = hd(order) - 1
			val front = List.nth(order, 1) 
			val behind = List.nth(order, 2)
			val new_map = union_after_behind(
							add_new(add_behind(List.nth(orders, person), front, behind), front, behind)
						 , front, behind)
		in
			generate_order_map(update_list(orders, hd(order)-1, new_map), remain) 
		end;
	

fun range(L) = 
	if L = 0 then []
	else range(L-1) @ [L];

fun mymap(f,L) = if L=[] then []
    else f(List.hd(L))::(mymap(f,List.tl(L)));

fun inter_leave(x, []) = [[x]]
	| inter_leave(x, h::t) = 
        (x::h::t) :: (mymap((fn l => h::l), inter_leave(x, t)));

fun appendAll(nil) = nil
	| appendAll(z::zs) = z @ (appendAll(zs));

fun permute(nil) = [[]]
	| permute(h::t) = 
		appendAll( mymap((fn l => inter_leave(h, l)), permute(t) ));

fun min(X,Y) = if X>Y then Y else X;

(* Count how many violations in the input order with the order_map*)
fun count_vio([], order_map) = 0
	| count_vio(h::t, order_map) = 
		(* From first place in the input list, create a set contains all elements behind it*)
		let	
			val place_set = IntListSet.addList(IntListSet.empty, t)
		in
			List.foldr (fn (x, y) => 
						(* In every map in the list, find if the front place exist in the map
							if exist, count # of place in person's set but not place set and sum
						*)
						let
							val person_set = IntListMap.find(x, h)
							val _ =
								if Option.isSome(person_set) then 
									IntListSet.listItems(Option.valOf(person_set))
								else []
						in
							if Option.isSome(person_set) then 
								IntListSet.numItems(IntListSet.difference(Option.valOf(person_set), place_set)) + y
							else y
						end
						) 
			0 order_map + count_vio(t, order_map)
		end;

(* Check all order violations in input int list list and find the smallest one*)
fun check_all([], order_map, min_vio) = min_vio 
	| check_all(h::t, order_map, min_vio) = 
		if min_vio = 0 then 0
		else if min_vio = ~1 then check_all(t, order_map, count_vio(h, order_map))
		else min(min_vio, check_all(t, order_map, count_vio(h, order_map)));

(* Generate data format needed and calculates the result*)
fun violations(NumberOfPeople:int, NumberOfLocations:int, NumberOfPreferences:int, Preferences: (int*int*int) list) = 
	let 
		val order_map = generate_order_map([], tuple2list(Preferences))
		val all_order = permute(range(NumberOfLocations))

	in
		check_all(all_order, order_map, ~1)
	end;

print(String.concat["violations(", Int.toString(violations(people, locations, preferences, orders_tuple)), ")\r\n" ] );

(* Escape interactive mode*)
val _ = OS.Process.exit(OS.Process.success);

