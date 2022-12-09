# concourseatom

This project provides a merge funtion to intelligently merge concourse jobs together.


# Rewrites in merge

When a pipeline is merging with another then it scans the names of the resources to identify it there are any duplicate resource types and if so then it plans rewrites of the Right Hand Side pipeine (on the merge funtion call). The process also scans for re-use of the same name for different resource types and plans similar rewrites for those as well.

This process is then similarily applied to resources.

Finally the rewrites are then applied to the jobs recursively to modify the resource types of the get and put names to match the resources.
It is also necessary to consider the name collisions of names of the handles of the resource not just there contents. These are identied as the objects that are the result of get and put and task mapped objects.


# Issues

Capture issues here to look at:

* [ ] In_parallel objects inside In_parallel objects. Seems to be triggering issues with sort order (may not be consistent) so results in comparisons of types that are not same.
