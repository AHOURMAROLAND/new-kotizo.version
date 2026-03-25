import React, { useEffect, useRef } from 'react';
import { Animated, Text, StyleSheet, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const ICONS = {
  success: { name: 'checkmark-circle', color: '#22C55E' },
  error: { name: 'close-circle', color: '#EF4444' },
  warning: { name: 'warning', color: '#F59E0B' },
  info: { name: 'information-circle', color: '#3B82F6' },
};

export default function KToast({ visible, message, type = 'success', onHide }) {
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 300, useNativeDriver: true }),
        Animated.delay(2500),
        Animated.timing(opacity, { toValue: 0, duration: 300, useNativeDriver: true }),
      ]).start(() => onHide && onHide());
    }
  }, [visible]);

  if (!visible) return null;
  const icon = ICONS[type] || ICONS.info;

  return (
    <Animated.View style={[styles.container, { opacity }]}>
      <Ionicons name={icon.name} size={20} color={icon.color} />
      <Text style={styles.text}>{message}</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 60,
    left: 20,
    right: 20,
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    zIndex: 9999,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 10,
  },
  text: { color: '#FFFFFF', fontSize: 14, flex: 1 },
});
