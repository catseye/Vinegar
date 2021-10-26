
    -> Tests for functionality "Execute Vinegar Program"

    -> Functionality "Execute Vinegar Program" is implemented by
    -> shell command
    -> "python3 bin/vinegar <%(test-body-file)"

Equal

    main = int[5] int[5] equal | int[4];
    ==> OK([])

Unequal

    main = int[5] int[8] equal | int[4];
    ==> OK([4])

Factorial

    main = int[5] fact;
    fact = dup int[1] equal | dup int[1] sub fact mul;
    ==> OK([120])

Failure

    main = swap;
    ==> Failure(underflow)

Pop

    main = int[40] int[50] pop int[60];
    ==> OK([40, 60])

Swap

    main = int[100] int[200] swap;
    ==> OK([200, 100])
