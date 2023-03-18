#import statements


def pings_blue_alliance():

	return


def evaluates_link(next_link, link_queue, link_set, verbose):
	if next_link in link_set():
		return
	html = pings_blue_alliance(next_link)


	if verbose:
		if len(link_set) % 100:
			print(f"Evaluated {len(link_set)} links.")
	return


def main():
	print("we finally getting somehwere")
	return
	#hyperparameter\
	verbose = True

	#static parameters
	base_link = "random junk"
	link_queue = queue(base_link)
	link_set = set(base_link)

	
	#Algorithm
	#while(link_queue not empty):
	#	next_link = queue.pop()
	#	evaluates_link(next_link, link_queue, link_set, verbose)
	return


if __name__ == "__main__":
	main()