#!/bin/python
"""# 20questions expert system

A tool to store, organize and optimize the triage of new tickets.

# Scheme

The system asks questions having n possible answers. You can either answer or decline. After sufficient, or all, questions have been asked, the system will offer any answers it can determine might apply, plus "other". If you select other, then you enter the answer that applies, and enter a discriminating question.


# Data types

An ordered list of questions lead to a set of outcomes. This can be modeled as a tree or a table.

The popularity of the questions' outcomes should be monitored to use huffman encoding to order the questions.

Looking at the tabular view:

Answer-set
ID  Q1  Q2  Q3  Q4  Q4  Outcome Frequency
1   y   ?   n   y   1       19
2   y   n   n   n   2       62

It should be possible to tell from the above that Q4 is key.

Integrity: if an outcome is not-known then it tentatively counts for all answers in that question. If some other answer-set has a ground term in that position, then it must be discernible, i.e. it must differ in some other ground term from a ground term in this set.

## Discernible:

Two answer sets are discernible if some answer in the set is discernible.

Two answers are discernible if both are ground terms and they differ.

NOTE: this means that an answer is not discernible from no-answer, since
no-answer is an implied non-ground term.

TODO:
    refactor!
    in "choose a course of action", allow the user to go ahead and type the new
        answer.
    write to/read from disk
    order suggestions with more-specific suggestions first.
    optimize sequence of asking questions

"""
import collections
import unittest


def keys_are_discernible( answer_set_left, answer_set_right ):
    for k in answer_set_left:
        if k in answer_set_right and \
                        answer_set_left[ k ] is not None and \
                        answer_set_right[ k ] is not None and \
                        answer_set_left[ k ] != answer_set_right[ k ]:
            return True
    return False


class TestDiscernible( unittest.TestCase ):
    def test1( self ):
        self.assertFalse(
            keys_are_discernible( { 'Q1': 'y' }, { 'Q1': None } ) )

    def test2( self ):
        self.assertFalse(
            keys_are_discernible( { 'Q1': 'y' }, { } ) )

    def test3( self ):
        self.assertFalse( keys_are_discernible( { 'Q1': 'y' }, { 'Q1': 'y' } ) )

    def test4( self ):
        self.assertTrue( keys_are_discernible( { 'Q1': 'y' }, { 'Q1': 'n' } ) )

    def test5( self ):
        self.assertFalse(
            keys_are_discernible( { 'Q1': None }, { 'Q1': 'n' } ) )


class AnswerSet( object ):
    """ An answer-set is a set of answers to the questions, and an outcome.
    """

    def __init__( self, qa, outcome ):
        """ qa is a dict { question_id: answer }
            outcome is an index into the outcomes list. """
        self._outcome = outcome
        self._qa = qa

    def match( self, keydict ):
        """ keydict contains a dict of { question_id:answer }

            It matches if it is not Discernible (see main docstring)
        """
        return not keys_are_discernible( self._qa, keydict )

    def get_key( self ):
        return self._qa

    def get_outcome( self ):
        return self._outcome


if __name__ == "__main__":

    questions = [ ]
    outcomes = [ '(other)' ]
    outcome_frequencies = collections.defaultdict( int )
    answer_sets = [ AnswerSet( { 0: None }, 0 ) ]

    while True:
        # TODO load data

        print "Triage expert: please answer some questions."
        # Run through all the questions to arrive at a key
        key = { }
        for id, q in enumerate( questions ):
            answer = raw_input( "{}. {}: ".format( id, q ) )
            key[ id ] = answer

        # What outcomes match our key? Store the indices in matching_outcomes, and
        # always include index 0.
        candidate_outcomes = set( )
        candidate_outcomes.add( 0 )
        for candidate_outcome in answer_sets:
            if candidate_outcome.match( key ):
                candidate_outcomes.add( candidate_outcome.get_outcome( ) )

        # Write out the candidate outcomes
        for n, o in enumerate( candidate_outcomes ):
            print n, outcomes[ o ]

        # Ask for the key of the chosen candidate
        choice = int( raw_input( 'Choose a course of action: ' ) )
        if choice:
            # The user selected an existing outcome. Note it
            outcome_frequencies[ choice ] += 1
        else:
            # The user said 'none of the above (below)'
            new_outcome = raw_input(
                'Please enter the correct outcome for this item: ' )
            if len( candidate_outcomes ) > 1:
                # We were offered more than zero options besides (other), so we need
                # a new question to discern
                question = raw_input(
                    'Please enter the question that would discriminate between this outcome and others: ' )
                answer = raw_input(
                    'Please enter the answer to that question for this outcome: ' )
                # Add the question to the database and extend the "where are we now?"
                # key with the new answer
                key[ len( questions ) ] = answer
                questions.append( question )
                print "New question is stored."

            # Add the outcome with the (potentially updated) "where are we now?" key
            answer_sets.append( AnswerSet( key, len( outcomes ) ) )
            outcomes.append( new_outcome )

        # TODO optimize
        # TODO store data
