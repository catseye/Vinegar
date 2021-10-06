Vinegar
=======

WIP
| _See also:_ [Tandem](https://github.com/catseye/Tandem)
∘ [Tamsin](https://github.com/catseye/Tamsin)
∘ [Carriage](https://github.com/catseye/Carriage)
∘ [Wanda](https://github.com/catseye/Wanda)

- - - -

### Overview

**Vinegar** is a semi-concatenative language where every operation can fail.

### Whence "semi-concatenative"?

Well, a concatenative language has a single binary operator with which one can
compose larger operations out of smaller operations, and that operator is
represented by no explicit symbol but rather just the juxtaposition
(concatenation) of operations.

The operations themselves are often functions that take stacks to stacks,
and the binary operator usually works rather a lot like function composition.

And since it's the only binary operator, and it's associative,
there are no parentheses, because there is no need for them.

Vinegar, in comparison, also has operations that work on stacks, and
an implicit binary operator that works a lot like function composition.
But it has another binary operator too, called _alternation_.  This one
is not implicit -- it's notated `|` and has a lower precedence than
concatenation -- and parentheses are available to group expressions.

This is not strictly speaking a concatenative language anymore, so we
call it "semi-concatenative".

(But later on we'll consider a variation on how things are arranged
here, that can make it all look "a bit more concatenative" again.)

### Whence "every operation can fail"?

This should be fairly intuitive -- when it is not possible for an
operation to produce a sensible, expected result, it has failed.

Division is the classic example, where division by zero is undefined,
and thus has failed.  But even addition can fail, if you consider
overflow of the machine integer size to be a failure.

And in a dynamically-typed stack-based language, such as concatenative
languages often are, any operation could potentially underflow the stack.
Which would be, y'know.  A failure.

In Vinegar, every operation can fail.  When faced with operations
that seem like they always succeed, we sometimes contrive them so that
there are ways that they can fail.  And in cases where we cannot be
bothered to do that, we just pretend there is a theoretical possibility
that they could fail.

The relevant question is, what happens when an operation fails?

Well, that's what `|` is for.

The next section attempts to describe the semantics of concatenation
and alternation in more detail.

### Concatenation and alternation

The rules of the concatenation operator are:

If, in `a b`, `a` fails, then `b` is not performed, and `a b`
fails with the error result produced by `a` failing.

If, in `a b`, `a` succeeds but `b` fails, then `a b`
fails with the error result produced by `b` failing.

If, in `a b`, `a` succeeds, then `b` succeeds, then `a b`
succeeds with the succesful result of `b` (which built
on the successful result of `a`).

The rules for the alternation operator are:

If, in `a | b`, `a` succeeds, then `b` is not performed, and
`a | b` succeeds with the result successfully produced by `a`.

If, in `a | b`, `a` fails, then `b` is performed, and the
result of `a | b` is the result of `b`.

If, in `a | b`, `a` fails, then `b` fails, then `a | b`
fails with the error result produced by `b` failing.

It's worth noting that both concatenation and alternation
are associative:

    (a b) c = a (b c) = a b c

and

    (a | b) | c = a | (b | c) = a | b | c

It's all a bit like `MonadPlus` in Haskell, with concatenation
being a lot like `>=>`, although I really had `Either` more
in mind than `Maybe`, but `Either` isn't an instance of
`MonadPlus` for technical reasons, and I don't understand
monads anyway I'm sure.

### The practical upshot of all this

With the alternation operator, we can implement exception handling.

In fact, in `a | b`, `b` probably should have some access to
`a`'s error result, if `a` failed.  An error result would be
like an error message or a traceback.  Indeed, the same sort
of information one would expect from an exception.

But here is another twist.  We can use alternation as a replacement
for `if...then...else` constructs: instead of checking _if_
an expression equals some value, we _assert_ that it _does_
equal some value.  If we happen to be wrong, then that is a failure.
We handle it on the RHS of a `|` just like we would handle any
other failure.  Rather than putting it in an `else` clause.

As a bonus, a chain like `a | b | c | d` is a terse
substitute for a chain of `elsif`s.

### Example: Factorial in Vinegar

As an example, let's try to write a factorial function in Vinegar.

    fact = dup <1> gt! dup <1> sub fact mul | nop

What we have here is:

Take the first "argument" to the `fact` function (with `dup`)
and assert (with `gt!`) that it is greater than 1.  Then take that
argument again (`dup` it again) and subtract one from it,
get the `fact` of that value, and multiply the argument
(itself - no `dup` this time) by that result.  And leave that
on the stack, as the result value.

If any operation there failed, we just perform no operation.
So for example, if our assertion that the argument was
greater than 1 failed, it will just leave the argument on
the stack, as the result value.

That's not actually fantastic.  What if `mul` failed?  In
that case we probably don't want to return whatever working
garbage happens to be on the stack as our result.  Rather,
we want to fail too.  So maybe we can write this more
pointifically.

    fact = dup <1> eq! | dup <1> sub fact mul

Now, we take the argument and assert that it *is* 1.  If
it is, we just return it.  If not, we compute factorial
on it, and return that.  If anything in our factorial
computation fails, `fact` itself fails, which is desirable.

Of course, this still breaks down if we're passed an
argument that is zero or negative.  What's the factorial
of such a number?  Let's say, for the sake of argument,
it's considered an error.  We can add that as an assertion.

    fact = dup <0> gt! (dup <1> eq! | dup <1> sub fact mul)

If it's 0 or negative, the `gt!` assertion fails, and
the whole thing fails.  If it's 1, the `eq!` assertion
doesn't fail, and 1 is returned.  If it's greater than
1, the `eq!` assertion fails and factorial is computed.

Note that we do need parentheses here so that when the
`gt!` fails, all of `fact` fails, instead of it falling
back to the operation on the RHS of the `|`.

Lastly, you may ask, why are there angle brackets around
the literal values 0 and 1?  That's so that literals can
fail; if it's not possible to parse the contents of a
`<...>` into a valid constant value, it has failed!

### A bit more concatenative

Fans of concatenative languages (concatenativophiles?
concatenativesters? concatenativeniks?) will no doubt
be disappointed at the appearance of an explicit binary
operator, and even *parentheses* (ugh), in this language.

But if we take some frightful measures, we may put some
distance between us and these pedestrian things.

If we want our binary operator to be notated by mere
juxtaposition, we obviously cannot have more than one
binary operator.  Yet here, in this language, we have two.

We surmount this obstacle by noting that, although
we have two binary operators in the *language*, we can
restrict each *definition* to having only one kind of
operator, and have multiple kinds of *definitions*.
In some definitions, concatenation is implicit; in
other definitions, alternation is implicit.

To be precise: A definition in which concatenation is implicit
is introduced with `=&`.  A definition in which alternation is
implicit is introduced with `=|`.

Armed with these facts, we can rewrite the above definition of
`fact` without infix operators and without parentheses
using multiple definitions, in this way:

    fact =& fac1 fac2
    fac1 =& dup <0> gt!
    fac2 =| fac3 fac4
    fac3 =& dup <1> eq!
    fac4 =& dup <1> sub fact mul

There!  Are you happy now?