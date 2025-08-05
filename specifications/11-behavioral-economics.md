# Behavioral Economics Specification

## Overview

This document specifies the behavioral economics framework for AgentGraphSociety, incorporating cognitive biases, bounded rationality, decision heuristics, and social economic behaviors that make agent decision-making more realistic.

## Core Concepts

### 1. Bounded Rationality Model

Agents have limited cognitive resources and cannot process all available information perfectly.

```python
class BoundedRationalityModel:
    """Model of limited cognitive capacity and information processing."""
    
    def __init__(self):
        self.cognitive_load: float = 0.0  # 0-1: current mental burden
        self.processing_capacity: float = 1.0  # 0-1: available capacity
        self.attention_span: float = 0.7  # 0-1: focus duration
        self.information_limit: int = 7  # Miller's law: 7±2 items
        
    def filter_information(self, 
                         information: List[Information],
                         personality: PersonalityProfile) -> List[Information]:
        """Filter information based on cognitive limits."""
        # Sort by salience and relevance
        scored_info = []
        for info in information:
            score = info.relevance
            
            # Recent information weighted higher (availability bias)
            recency_weight = 1.0 - (time.time() - info.timestamp) / 86400
            score *= (0.7 + 0.3 * recency_weight)
            
            # Emotional salience
            if info.emotional_valence > 0.7:
                score *= 1.5
            
            # Personality affects attention
            if personality.openness > 0.7:
                score *= 1.2  # More receptive to new info
            
            scored_info.append((info, score))
        
        # Return top items within cognitive limit
        sorted_info = sorted(scored_info, key=lambda x: x[1], reverse=True)
        return [info for info, _ in sorted_info[:self.information_limit]]
    
    def calculate_decision_quality(self) -> float:
        """Quality of decisions decreases with cognitive load."""
        if self.cognitive_load < 0.3:
            return 0.95  # Low load, good decisions
        elif self.cognitive_load < 0.7:
            return 0.8 - (self.cognitive_load - 0.3) * 0.5
        else:
            return 0.5  # High load, poor decisions
```

### 2. Cognitive Biases Implementation

```python
class CognitiveBiasEngine:
    """Implements various cognitive biases affecting decisions."""
    
    def __init__(self, agent_profile: AgentProfile):
        self.agent = agent_profile
        self.bias_strengths = self._initialize_bias_strengths()
    
    def _initialize_bias_strengths(self) -> Dict[str, float]:
        """Individual variation in bias susceptibility."""
        return {
            "confirmation_bias": 0.3 + self.agent.personality.neuroticism * 0.4,
            "anchoring_bias": 0.4 + (1 - self.agent.personality.openness) * 0.3,
            "availability_heuristic": 0.5,
            "loss_aversion": 0.6 + self.agent.personality.neuroticism * 0.3,
            "social_proof": 0.4 + self.agent.personality.agreeableness * 0.4,
            "sunk_cost_fallacy": 0.5 + self.agent.personality.conscientiousness * 0.2,
            "framing_effect": 0.4,
            "overconfidence": 0.3 + self.agent.personality.extraversion * 0.3
        }
    
    def apply_confirmation_bias(self, 
                               information: List[Information],
                               beliefs: Dict[str, float]) -> List[Information]:
        """Filter information that confirms existing beliefs."""
        bias_strength = self.bias_strengths["confirmation_bias"]
        
        filtered = []
        for info in information:
            # Calculate alignment with existing beliefs
            alignment = self._calculate_belief_alignment(info, beliefs)
            
            # Bias towards confirming information
            if alignment > 0:
                acceptance_prob = 0.5 + alignment * bias_strength
            else:
                acceptance_prob = 0.5 - abs(alignment) * bias_strength
            
            if random.random() < acceptance_prob:
                filtered.append(info)
        
        return filtered
    
    def apply_loss_aversion(self, 
                           gains: float, 
                           losses: float) -> float:
        """Losses feel worse than equivalent gains feel good."""
        bias_strength = self.bias_strengths["loss_aversion"]
        
        # Typical loss aversion ratio is 2:1
        loss_weight = 1.5 + bias_strength
        
        utility = gains - (losses * loss_weight)
        return utility
    
    def apply_anchoring_bias(self,
                            value: float,
                            anchor: float) -> float:
        """Estimates biased towards initial anchor value."""
        bias_strength = self.bias_strengths["anchoring_bias"]
        
        # Adjust estimate towards anchor
        adjusted = value + (anchor - value) * bias_strength
        return adjusted
    
    def apply_social_proof(self,
                          own_preference: float,
                          group_behavior: float,
                          group_size: int) -> float:
        """Adjust preference based on what others are doing."""
        bias_strength = self.bias_strengths["social_proof"]
        
        # Larger groups have more influence
        group_influence = min(1.0, group_size / 50) * bias_strength
        
        # Adjust own preference towards group
        adjusted = own_preference + (group_behavior - own_preference) * group_influence
        return adjusted
```

### 3. Prospect Theory Implementation

```python
class ProspectTheoryModel:
    """Kahneman & Tversky's prospect theory for decision under risk."""
    
    @staticmethod
    def probability_weighting(p: float) -> float:
        """
        Transform objective probabilities to decision weights.
        People overweight small probabilities and underweight large ones.
        """
        if p == 0:
            return 0
        if p == 1:
            return 1
        
        # Tversky & Kahneman (1992) weighting function
        gamma = 0.61  # For gains
        return (p ** gamma) / ((p ** gamma + (1 - p) ** gamma) ** (1 / gamma))
    
    @staticmethod
    def value_function(x: float, reference_point: float = 0) -> float:
        """
        S-shaped value function: concave for gains, convex for losses.
        Losses loom larger than gains.
        """
        relative_value = x - reference_point
        
        if relative_value >= 0:
            # Gains: risk averse (concave)
            alpha = 0.88
            return relative_value ** alpha
        else:
            # Losses: risk seeking (convex) and stronger impact
            beta = 0.88
            lambda_loss = 2.25  # Loss aversion coefficient
            return -lambda_loss * ((-relative_value) ** beta)
    
    def evaluate_prospect(self, 
                         outcomes: List[Tuple[float, float]],
                         reference_point: float) -> float:
        """
        Evaluate a risky prospect using prospect theory.
        outcomes: List of (probability, value) tuples
        """
        total_value = 0
        
        for prob, value in outcomes:
            # Weight the probability
            decision_weight = self.probability_weighting(prob)
            
            # Transform the value
            subjective_value = self.value_function(value, reference_point)
            
            # Add to total
            total_value += decision_weight * subjective_value
        
        return total_value
```

### 4. Heuristics and Mental Models

```python
class DecisionHeuristics:
    """Fast and frugal heuristics for common decisions."""
    
    @staticmethod
    def satisficing(options: List[Option], 
                   aspiration_level: float) -> Optional[Option]:
        """
        Select first option that meets aspiration level.
        Simon's satisficing heuristic.
        """
        for option in options:
            if option.utility >= aspiration_level:
                return option
        
        # If none meet aspiration, lower it
        return max(options, key=lambda x: x.utility)
    
    @staticmethod
    def elimination_by_aspects(options: List[Option],
                              aspects: List[Aspect]) -> Option:
        """
        Eliminate options that don't meet criteria on key aspects.
        Tversky's elimination heuristic.
        """
        remaining = options.copy()
        
        for aspect in aspects:
            # Filter options meeting this aspect's minimum
            remaining = [opt for opt in remaining 
                        if opt.get_aspect_value(aspect) >= aspect.minimum]
            
            if len(remaining) == 1:
                return remaining[0]
            elif len(remaining) == 0:
                # Too strict, return best on this aspect
                return max(options, key=lambda x: x.get_aspect_value(aspect))
        
        # Multiple options remain, pick randomly
        return random.choice(remaining)
    
    @staticmethod
    def recognition_heuristic(options: List[Option],
                             recognition_scores: Dict[str, float]) -> Option:
        """
        Choose recognized option over unrecognized.
        Goldstein & Gigerenzer's recognition heuristic.
        """
        recognized = [(opt, recognition_scores.get(opt.id, 0)) 
                     for opt in options]
        recognized.sort(key=lambda x: x[1], reverse=True)
        
        # If clear recognition difference, choose recognized
        if recognized[0][1] > 0.7 and recognized[1][1] < 0.3:
            return recognized[0][0]
        
        # Otherwise, need more analysis
        return None
```

### 5. Social Economic Behaviors

```python
class SocialEconomicBehavior:
    """Social influences on economic decisions."""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.fairness_preference = self._init_fairness_preference()
        self.reciprocity_tendency = self._init_reciprocity()
        self.social_comparison_sensitivity = self._init_social_comparison()
    
    def _init_fairness_preference(self) -> float:
        """How much agent cares about fairness."""
        return 0.3 + self.agent.personality.agreeableness * 0.5
    
    def _init_reciprocity(self) -> float:
        """Tendency to reciprocate others' actions."""
        return 0.4 + self.agent.personality.agreeableness * 0.3 + \
               self.agent.values.get("tradition", 0.5) * 0.2
    
    def _init_social_comparison(self) -> float:
        """Sensitivity to relative position."""
        return 0.3 + self.agent.personality.neuroticism * 0.3 + \
               self.agent.values.get("social_status", 0.5) * 0.3
    
    def evaluate_fairness(self, 
                         my_share: float,
                         other_share: float,
                         total: float) -> float:
        """Evaluate fairness of a distribution."""
        if total == 0:
            return 0.5
        
        my_proportion = my_share / total
        other_proportion = other_share / total
        
        # Deviation from equal split
        inequality = abs(my_proportion - 0.5)
        
        # Fairness-adjusted utility
        raw_utility = my_share
        fairness_penalty = inequality * self.fairness_preference * total
        
        # Advantageous vs disadvantageous inequality
        if my_proportion > 0.5:
            # Feel less bad about advantageous inequality
            fairness_penalty *= 0.5
        
        return raw_utility - fairness_penalty
    
    def reciprocate_action(self,
                          other_agent: int,
                          their_action: Action,
                          history: List[Interaction]) -> Action:
        """Reciprocate based on past interactions."""
        # Calculate cooperation score from history
        cooperation_score = self._calculate_cooperation_score(
            other_agent, 
            history
        )
        
        # Strong reciprocity: cooperate with cooperators, punish defectors
        if cooperation_score > 0.7:
            return Action("cooperate", strength=0.8)
        elif cooperation_score < 0.3:
            if self.reciprocity_tendency > 0.6:
                return Action("punish", strength=0.6)
            else:
                return Action("defect", strength=0.4)
        else:
            # Neutral: match their action
            return their_action
    
    def social_comparison_utility(self,
                                 my_outcome: float,
                                 reference_group_outcomes: List[float]) -> float:
        """Utility affected by comparison to others."""
        # Calculate relative position
        avg_others = np.mean(reference_group_outcomes)
        relative_position = (my_outcome - avg_others) / (avg_others + 1)
        
        # Base utility
        utility = my_outcome
        
        # Social comparison adjustment
        if relative_position > 0:
            # Positive: satisfaction from being above average
            utility += relative_position * self.social_comparison_sensitivity * 20
        else:
            # Negative: stronger dissatisfaction from being below
            utility += relative_position * self.social_comparison_sensitivity * 30
        
        return utility
```

### 6. Time Preferences and Discounting

```python
class TemporalDiscounting:
    """Models how agents value future vs present rewards."""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.base_discount_rate = self._calculate_base_discount()
        self.present_bias_strength = self._calculate_present_bias()
    
    def _calculate_base_discount(self) -> float:
        """Individual discount rate based on personality."""
        # High conscientiousness = more patient (lower discount)
        # High neuroticism = more impatient (higher discount)
        return 0.1 + \
               (1 - self.agent.personality.conscientiousness) * 0.2 + \
               self.agent.personality.neuroticism * 0.1
    
    def _calculate_present_bias(self) -> float:
        """Hyperbolic discounting strength."""
        return 0.5 + (1 - self.agent.personality.conscientiousness) * 0.3
    
    def discount_future_value(self,
                            value: float,
                            delay_days: int) -> float:
        """Apply temporal discounting to future rewards."""
        if delay_days == 0:
            return value
        
        # Quasi-hyperbolic discounting (β-δ model)
        if delay_days == 1:
            # Immediate future discounted more
            beta = 1 - self.present_bias_strength * 0.3
            return value * beta
        else:
            # Standard exponential for further future
            daily_discount = 1 - self.base_discount_rate / 365
            return value * (daily_discount ** delay_days)
    
    def choose_temporal_option(self,
                             immediate_reward: float,
                             delayed_reward: float,
                             delay_days: int) -> str:
        """Choose between immediate and delayed rewards."""
        # Discount the delayed reward
        discounted_delayed = self.discount_future_value(
            delayed_reward, 
            delay_days
        )
        
        # Add noise for realistic variation
        immediate_utility = immediate_reward * random.uniform(0.9, 1.1)
        delayed_utility = discounted_delayed * random.uniform(0.9, 1.1)
        
        if immediate_utility > delayed_utility:
            return "immediate"
        else:
            return "delayed"
```

## Integration with Agent Decision Making

### 1. Economic Decision Block

```python
class EconomicDecisionBlock(Block):
    """Make economic decisions using behavioral economics principles."""
    
    name = "EconomicDecisionBlock"
    description = "Behavioral economics-based decision making"
    
    async def forward(self, context: DotDict):
        # Initialize components
        bounded_rationality = BoundedRationalityModel()
        bias_engine = CognitiveBiasEngine(self.agent)
        prospect_model = ProspectTheoryModel()
        
        # Get decision context
        decision_type = context.get("decision_type")
        options = context.get("options", [])
        
        # Apply bounded rationality
        if len(options) > bounded_rationality.information_limit:
            # Use heuristic for too many options
            options = self._apply_heuristic_filtering(options)
        
        # Apply relevant biases
        if decision_type == "purchase":
            # Anchoring on first price seen
            if hasattr(self.agent, "price_anchor"):
                options = self._apply_anchoring_to_prices(
                    options, 
                    self.agent.price_anchor,
                    bias_engine
                )
        
        # Evaluate options using prospect theory
        reference_point = await self._get_reference_point()
        evaluated_options = []
        
        for option in options:
            # Convert to prospects
            outcomes = self._option_to_outcomes(option)
            value = prospect_model.evaluate_prospect(outcomes, reference_point)
            evaluated_options.append((option, value))
        
        # Make final choice
        if random.random() < 0.1:  # 10% random choice
            choice = random.choice(options)
        else:
            choice = max(evaluated_options, key=lambda x: x[1])[0]
        
        return {
            "success": True,
            "choice": choice,
            "decision_quality": bounded_rationality.calculate_decision_quality()
        }
```

### 2. Market Behavior Integration

```python
class MarketBehaviorBlock(Block):
    """Simulate market behavior with behavioral economics."""
    
    async def forward(self, context: DotDict):
        market_info = context.get("market_info")
        
        # Herding behavior
        if market_info.trend_strength > 0.7:
            # Strong trend triggers herding
            herd_probability = 0.3 + self.agent.personality.agreeableness * 0.4
            if random.random() < herd_probability:
                return {
                    "action": "follow_trend",
                    "reason": "social_proof"
                }
        
        # Disposition effect: hold losers too long, sell winners too early
        portfolio = await self.agent.get_portfolio()
        for asset in portfolio:
            if asset.unrealized_gain > 0.2:
                # Tendency to sell winners
                sell_prob = 0.4 + (1 - self.agent.personality.openness) * 0.3
                if random.random() < sell_prob:
                    return {
                        "action": "sell",
                        "asset": asset.id,
                        "reason": "disposition_effect"
                    }
            elif asset.unrealized_loss > 0.2:
                # Tendency to hold losers
                hold_prob = 0.7 + self.agent.personality.neuroticism * 0.2
                if random.random() < hold_prob:
                    return {
                        "action": "hold",
                        "asset": asset.id,
                        "reason": "loss_aversion"
                    }
        
        return {"action": "no_action"}
```

## Neo4j Integration

### 1. Behavioral Economics Properties

```cypher
// Add to Agent node
(:Agent {
  // Existing properties...
  
  // Behavioral economics traits
  risk_tolerance: Float,           // 0-1: willingness to take risks
  loss_aversion_strength: Float,   // 1-3: how much losses hurt
  discount_rate: Float,            // 0-1: time preference
  fairness_preference: Float,      // 0-1: concern for fairness
  
  // Decision history
  decision_quality_avg: Float,     // Average decision quality
  bias_susceptibility: Float,      // 0-1: overall bias tendency
  heuristic_usage: Float          // 0-1: reliance on heuristics
})
```

### 2. Economic Relationships

```cypher
// Economic trust relationship
(:Agent)-[:TRUSTS_ECONOMICALLY {
  trust_level: Float,            // 0-1: economic trust
  transaction_history: String,   // JSON: past transactions
  reciprocity_score: Float,      // -1 to 1: reciprocal behavior
  
  // Game theory outcomes
  cooperation_rate: Float,       // 0-1: how often cooperates
  defection_cost: Float,         // Cost of their defection
  
  last_interaction: DateTime,
  total_interactions: Integer
}]->(:Agent)

// Market influence relationship
(:Agent)-[:INFLUENCES_MARKET_BEHAVIOR {
  influence_strength: Float,     // 0-1: market influence
  information_quality: Float,    // 0-1: quality of their info
  
  // Herding metrics
  followed_count: Integer,       // Times others followed
  contrarian_actions: Integer,   // Times went against
  
  domains: [String]             // Market domains influenced
}]->(:Agent)
```

### 3. Decision History Tracking

```cypher
(:Decision {
  id: String,
  agent_id: Integer,
  timestamp: DateTime,
  
  // Decision details
  type: String,                  // "purchase", "investment", etc.
  options_considered: Integer,
  choice_made: String,
  
  // Behavioral factors
  cognitive_load: Float,         // At time of decision
  biases_active: [String],       // Active biases
  heuristic_used: String,        // If any
  
  // Outcomes
  immediate_outcome: Float,
  long_term_outcome: Float,
  regret_level: Float           // Post-decision regret
})

(:Agent)-[:MADE_DECISION {
  quality_score: Float,          // Decision quality
  time_taken: Integer,           // Seconds to decide
  confidence: Float              // 0-1: decision confidence
}]->(:Decision)
```

## Implementation Guidelines

### 1. Bias Calibration

- Individual variation: Not all agents equally susceptible to biases
- Cultural factors: Some biases vary by cultural background
- Learning: Agents can partially learn to overcome biases
- Stress effects: Biases stronger under stress/cognitive load

### 2. Market Dynamics

- Information cascades: Early movers influence later decisions
- Bubble formation: Positive feedback loops in markets
- Panic selling: Contagion effects during downturns
- Price anchoring: Initial prices strongly influence valuations

### 3. Realism Constraints

- Bounded wealth: Agents have limited resources
- Information costs: Gathering information has costs
- Social pressure: Deviation from norms has social costs
- Reputation effects: Past behavior affects future interactions

## Testing Scenarios

### 1. Ultimatum Game
Test fairness preferences and social considerations in economic decisions.

### 2. Public Goods Game
Test cooperation, free-riding, and reciprocity in group settings.

### 3. Market Bubbles
Test herding behavior and information cascades in market scenarios.

### 4. Intertemporal Choice
Test time preferences and present bias in savings/consumption decisions.

### 5. Risk Scenarios
Test prospect theory predictions under gains vs losses framing.